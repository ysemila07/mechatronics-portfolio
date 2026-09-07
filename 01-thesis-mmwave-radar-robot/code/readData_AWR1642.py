# Handle serial communication with radar module and parse detected object data streams.
import os, sys, time, glob, serial
import numpy as np

HEADLESS = True             # set as; True = no GUI, False = with GUI
CFG_FILE = "1642config.cfg" # radar config file used

# GUI dependencies
if not HEADLESS:
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtWidgets

# Serial helpers
def find_cli_and_data_ports():
    candidates = []
    for pattern in ("/dev/ttyACM*", "/dev/ttyUSB*"):
        candidates.extend(sorted(glob.glob(pattern)))
    for i in range(len(candidates)-1):
        a, b = candidates[i], candidates[i+1]
        try:
            cli = serial.Serial(a, 115200, timeout=0.2); cli.close()
            dat = serial.Serial(b, 921600, timeout=0.2); dat.close()
            return a, b
        except Exception:
            pass
    if len(candidates) >= 2:
        return candidates[0], candidates[1]
    raise RuntimeError("Could not find two serial ports for radar (CLI + DATA).")

def open_ports():
    cli_port, dat_port = find_cli_and_data_ports()
    print(f"CLI : {cli_port} @115200")
    print(f"DATA: {dat_port} @921600")
    cli  = serial.Serial(cli_port, 115200, timeout=0.25)
    data = serial.Serial(dat_port, 921600, timeout=0.01)
    # Flush any junk before sending commands
    cli.reset_input_buffer();  cli.reset_output_buffer()
    data.reset_input_buffer(); data.reset_output_buffer()
    time.sleep(0.05)
    return cli, data

# Send config to the radar
def send_cli(cli, line):
    cli.write((line.strip() + "\n").encode("utf-8"))
    time.sleep(0.01)
    try:
        sys.stdout.write(cli.read_all().decode(errors="ignore"))
    except Exception:
        pass

def apply_cfg(cli, cfg_path):
    # extra flush before starting
    cli.reset_input_buffer(); cli.reset_output_buffer()
    time.sleep(0.02)

    send_cli(cli, "sensorStop")
    send_cli(cli, "flushCfg")

    saw_start = False
    with open(cfg_path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("%"):
                continue
            if line.lower().startswith("sensorstart"):
                saw_start = True
            send_cli(cli, line)

    if not saw_start:
        send_cli(cli, "sensorStart")

# Parse (structuring unorganised data) radar UART (detected points)
MMWDEMO_UART_MSG_DETECTED_POINTS = 1
MAGIC = np.array([2,1,4,3,6,5,8,7], dtype=np.uint8)
MAX_BUF = 2**15

byteBuffer = np.zeros(MAX_BUF, dtype=np.uint8)
byteBufferLength = 0

def readAndParseData16xx(dataport, config):
    global byteBuffer, byteBufferLength

    readBytes = dataport.read(dataport.in_waiting or 1024)
    if not readBytes:
        return 0, 0, {}

    byteVec = np.frombuffer(readBytes, dtype=np.uint8)
    n = len(byteVec)

    if (byteBufferLength + n) < MAX_BUF:
        byteBuffer[byteBufferLength:byteBufferLength+n] = byteVec
        byteBufferLength += n
    else:
        byteBufferLength = 0
        return 0, 0, {}

    if byteBufferLength < 48:
        return 0, 0, {}

    possible = np.where(byteBuffer[:byteBufferLength-7] == MAGIC[0])[0]
    startIdx = None
    for loc in possible:
        if np.all(byteBuffer[loc:loc+8] == MAGIC):
            startIdx = loc
            break
    if startIdx is None:
        return 0, 0, {}

    if startIdx > 0:
        byteBuffer[:byteBufferLength-startIdx] = byteBuffer[startIdx:byteBufferLength]
        byteBufferLength -= startIdx

    def u32(off):
        return int(byteBuffer[off] + (byteBuffer[off+1]<<8) + (byteBuffer[off+2]<<16) + (byteBuffer[off+3]<<24))

    if byteBufferLength < 48:
        return 0, 0, {}
    totalPacketLen = u32(12)
    if byteBufferLength < totalPacketLen:
        return 0, 0, {}

    idx = 0
    idx += 8   
    version = u32(idx); idx += 4
    totalPacketLen = u32(idx); idx += 4
    platform = u32(idx); idx += 4
    frameNumber = u32(idx); idx += 4
    timeCpuCycles = u32(idx); idx += 4
    numDetectedObj = u32(idx); idx += 4
    numTLVs = u32(idx); idx += 4
    subFrameNumber = u32(idx); idx += 4

    detObj = {}
    dataOK = 0

    for _ in range(numTLVs):
        if idx + 8 > totalPacketLen:
            break
        tlv_type = u32(idx);       idx += 4
        tlv_length = u32(idx);     idx += 4

        if tlv_type == MMWDEMO_UART_MSG_DETECTED_POINTS:
            if idx + 4 > totalPacketLen:
                break
            tlv_numObj = int(byteBuffer[idx] + (byteBuffer[idx+1]<<8)); idx += 2
            qFormat    = int(byteBuffer[idx] + (byteBuffer[idx+1]<<8)); idx += 2
            qScale = float(2**qFormat)

            if tlv_numObj > 0 and idx + tlv_numObj*12 <= totalPacketLen:
                objs = byteBuffer[idx: idx + tlv_numObj*12].view(np.int16).reshape((-1,6))
                idx += tlv_numObj*12

                rangeIdx  = objs[:,0].astype(np.int16)
                dopplerIx = objs[:,1].astype(np.int16)
                peakVal   = objs[:,2].astype(np.int16)
                x_q       = objs[:,3].astype(np.int16)
                y_q       = objs[:,4].astype(np.int16)
                z_q       = objs[:,5].astype(np.int16)

                rangeVal = rangeIdx * config["rangeIdxToMeters"]
                dopplerIx[dopplerIx > (config["numDopplerBins"]/2 - 1)] -= 65535
                dopplerVal = dopplerIx * config["dopplerResolutionMps"]
                x = x_q / qScale
                y = y_q / qScale
                z = z_q / qScale

                detObj = {
                    "numObj": tlv_numObj,
                    "rangeIdx": rangeIdx, "range": rangeVal,
                    "dopplerIdx": dopplerIx, "doppler": dopplerVal,
                    "peakVal": peakVal, "x": x, "y": y, "z": z
                }
                dataOK = 1
            else:
                idx += max(0, tlv_length - 4)
        else:
            idx += max(0, tlv_length - 8)

    if totalPacketLen <= byteBufferLength:
        byteBuffer[:byteBufferLength - totalPacketLen] = byteBuffer[totalPacketLen:byteBufferLength]
        byteBufferLength -= totalPacketLen
        if byteBufferLength < 0:
            byteBufferLength = 0

    return dataOK, frameNumber, detObj

# Parse config for radar parameters
def parseConfigFile(cfg_path):
    cfg = [ln.strip() for ln in open(cfg_path) if ln.strip() and not ln.strip().startswith("%")]
    numRxAnt, numTxAnt = 4, 2
    digOutSampleRate = 2000
    freqSlopeConst = 100
    numAdcSamples = 64
    idleTime = 7
    rampEndTime = 40
    startFreq = 77
    chirpStartIdx = chirpEndIdx = 0
    numLoops = 1

    for line in cfg:
        parts = line.split()
        if parts[0] == "profileCfg":
            startFreq        = float(parts[2])
            idleTime         = int(parts[3])
            rampEndTime      = float(parts[5])
            freqSlopeConst   = float(parts[8])
            numAdcSamples    = int(parts[10])
            digOutSampleRate = int(parts[11])
        elif parts[0] == "frameCfg":
            chirpStartIdx    = int(parts[1])
            chirpEndIdx      = int(parts[2])
            numLoops         = int(parts[3])

    nrb = 1
    while nrb < numAdcSamples:
        nrb *= 2

    numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
    numDopplerBins = numChirpsPerFrame / numTxAnt

    cfg_params = {}
    cfg_params["numRangeBins"] = nrb
    cfg_params["numDopplerBins"] = numDopplerBins
    cfg_params["rangeResolutionMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numAdcSamples)
    cfg_params["rangeIdxToMeters"]      = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * nrb)
    cfg_params["dopplerResolutionMps"]  = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * numDopplerBins * numTxAnt)
    return cfg_params

# Library generator for integration
def stream_points(cfg_path=CFG_FILE, headless=True):
    """
    Open ports, apply cfg, then yield per-frame points as (x,y,z,v,snr) lists (headless).
    """
    global HEADLESS
    HEADLESS = bool(headless)
    cli, data = open_ports()
    try:
        apply_cfg(cli, cfg_path)
        cfg_params = parseConfigFile(cfg_path)
        while True:
            ok, frame_no, det = readAndParseData16xx(data, cfg_params)
            if ok and det.get("numObj", 0) > 0:
                pts = list(zip(det["x"], det["y"], det["z"], det["doppler"], det["peakVal"]))
                yield pts
            else:
                yield []
            time.sleep(0.005)
    finally:
        try:
            send_cli(cli, "sensorStop")
        except Exception:
            pass
        cli.close()
        data.close()

# Main
def main():
    try:
        cli, data = open_ports()
    except Exception as e:
        print(f"[Port error] {e}")
        sys.exit(1)

    print("Applying config…")
    apply_cfg(cli, CFG_FILE)
    print("Config sent. Streaming… (Ctrl+C to stop)")

    cfg_params = parseConfigFile(CFG_FILE)

    if not HEADLESS:
        app = QtWidgets.QApplication([])
        pg.setConfigOption('background', 'w')
        win = pg.GraphicsLayoutWidget(title="AWR1642 Detected Points (XZ)")
        plt = win.addPlot()
        plt.setLabel('left', 'Y (m)')
        plt.setLabel('bottom', 'X (m)')
        plt.setXRange(-1.5, 1.5)
        plt.setYRange(0, 3.0)
        scatter = plt.plot([], [], pen=None, symbol='o')
        win.show()

    try:
        while True:
            ok, frame_no, det = readAndParseData16xx(data, cfg_params)
            if ok:
                if HEADLESS:
                    print(f"Frame {frame_no}: {det['numObj']} points")
                else:
                    x = -det["x"]
                    y = det["y"]
                    scatter.setData(x, y)
                    QtWidgets.QApplication.processEvents()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            send_cli(cli, "sensorStop")
        except Exception:
            pass
        cli.close()
        data.close()

if __name__ == "__main__":
    main()

# Radar thread for integration
import threading

class RadarThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        from readData_AWR1642 import open_ports, apply_cfg, parseConfigFile, readAndParseData16xx
        self.open_ports = open_ports
        self.apply_cfg = apply_cfg
        self.parseConfigFile = parseConfigFile
        self.readAndParseData16xx = readAndParseData16xx
        self.cfg_file = "1642config.cfg"
        self.cli = None
        self.data = None
        self.cfg_params = None
        self.running = False
        self.latest_points = []

    def run(self):
        try:
            self.cli, self.data = self.open_ports()
            print("[RadarThread] Ports opened.")
            self.apply_cfg(self.cli, self.cfg_file)
            self.cfg_params = self.parseConfigFile(self.cfg_file)
            print("[RadarThread] Config applied. Streaming...")
            self.running = True

            while self.running:
                ok, frame_no, det = self.readAndParseData16xx(self.data, self.cfg_params)
                if ok:
                    pts = []
                    for i in range(det["numObj"]):
                        pts.append((float(det["x"][i]),
                                    float(det["y"][i]),
                                    float(det["z"][i]),
                                    float(det["doppler"][i]),
                                    float(det["peakVal"][i])))
                    self.latest_points = pts
                time.sleep(0.01)

        except Exception as e:
            print(f"[RadarThread ERROR] {e}")
        finally:
            try:
                self.cli.close()
                self.data.close()
            except Exception:
                pass
            print("[RadarThread] Closed.")

    def get_points(self):
        return list(self.latest_points)

    def stop(self):
        self.running = False
        try:
            self.cli.write(b"sensorStop\n")
        except Exception:
            pass
        print("[RadarThread] Stopping stream...")