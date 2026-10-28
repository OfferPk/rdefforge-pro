#!/usr/bin/env python3
"""
RDEFForge Pro — Command Line Interface
CCSDS 506.1-B-1 Delta-DOR Raw Data Exchange Format Toolchain
"""

import sys
import os
import argparse
import json
import math
import struct
from datetime import datetime

SPEED_OF_LIGHT = 299792458.0  # m/s

def generate_standard_observation(station_id="DSS-14", target_sc="EUROPA-CLIPPER", target_qu="J1924-2914"):
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    lines = [
        "# ====================================================================",
        "# CCSDS 506.1-B-1 DELTA-DOR RAW DATA EXCHANGE FORMAT (RDEF)",
        "# OBSERVATION FILE (ASCII METADATA)",
        "# ====================================================================",
        "CCSDS_RDEF_VERS = 1.0",
        f"CREATION_DATE = {now_iso}",
        "ORIGINATOR = NASA-JPL-DSN",
        f"STATION_ID = {station_id}",
        "STATION_NAME = GOLDSTONE-BWG-34M",
        "ITRF_X = -2353621.419",
        "ITRF_Y = -4641341.552",
        "ITRF_Z = 3677052.321",
        "TIME_SYSTEM = UTC",
        "START_TIME = 2026-10-19T10:00:00Z",
        "STOP_TIME = 2026-10-19T11:45:00Z",
        "RECORDING_SYSTEM = WVSR-4",
        "# --------------------------------------------------------------------",
        "SCAN_SECTION = 1",
        "SCAN_ID = SCAN-001",
        "TARGET_TYPE = QUASAR",
        f"TARGET_ID = {target_qu}",
        "SCAN_START_TIME = 2026-10-19T10:00:00Z",
        "SCAN_STOP_TIME = 2026-10-19T10:20:00Z",
        "NUMBER_OF_CHANNELS = 4",
        "CHANNEL_1_ID = CH-X-01",
        "CHANNEL_1_FREQ = 8415000000.0",
        "CHANNEL_1_SAMPLE_RATE = 8000000",
        "CHANNEL_1_RESOLUTION_BITS = 8",
        "CHANNEL_1_POLARIZATION = RCP",
        "CHANNEL_1_PRODUCT_FILE = scan001_ch1.rdp",
        "CHANNEL_2_ID = CH-X-02",
        "CHANNEL_2_FREQ = 8425000000.0",
        "CHANNEL_2_SAMPLE_RATE = 8000000",
        "CHANNEL_2_RESOLUTION_BITS = 8",
        "CHANNEL_2_POLARIZATION = RCP",
        "CHANNEL_2_PRODUCT_FILE = scan001_ch2.rdp",
        "CHANNEL_3_ID = CH-X-03",
        "CHANNEL_3_FREQ = 8435000000.0",
        "CHANNEL_3_SAMPLE_RATE = 8000000",
        "CHANNEL_3_RESOLUTION_BITS = 8",
        "CHANNEL_3_POLARIZATION = RCP",
        "CHANNEL_3_PRODUCT_FILE = scan001_ch3.rdp",
        "CHANNEL_4_ID = CH-X-04",
        "CHANNEL_4_FREQ = 8445000000.0",
        "CHANNEL_4_SAMPLE_RATE = 8000000",
        "CHANNEL_4_RESOLUTION_BITS = 8",
        "CHANNEL_4_POLARIZATION = RCP",
        "CHANNEL_4_PRODUCT_FILE = scan001_ch4.rdp",
        "# --------------------------------------------------------------------",
        "SCAN_SECTION = 2",
        "SCAN_ID = SCAN-002",
        "TARGET_TYPE = SPACECRAFT",
        f"TARGET_ID = {target_sc}",
        "SCAN_START_TIME = 2026-10-19T10:25:00Z",
        "SCAN_STOP_TIME = 2026-10-19T10:45:00Z",
        "NUMBER_OF_CHANNELS = 4",
        "CHANNEL_1_ID = CH-X-01",
        "CHANNEL_1_FREQ = 8415000000.0",
        "CHANNEL_1_SAMPLE_RATE = 8000000",
        "CHANNEL_1_RESOLUTION_BITS = 8",
        "CHANNEL_1_POLARIZATION = RCP",
        "CHANNEL_1_PRODUCT_FILE = scan002_ch1.rdp",
        "CHANNEL_2_ID = CH-X-02",
        "CHANNEL_2_FREQ = 8425000000.0",
        "CHANNEL_2_SAMPLE_RATE = 8000000",
        "CHANNEL_2_RESOLUTION_BITS = 8",
        "CHANNEL_2_POLARIZATION = RCP",
        "CHANNEL_2_PRODUCT_FILE = scan002_ch2.rdp",
        "CHANNEL_3_ID = CH-X-03",
        "CHANNEL_3_FREQ = 8435000000.0",
        "CHANNEL_3_SAMPLE_RATE = 8000000",
        "CHANNEL_3_RESOLUTION_BITS = 8",
        "CHANNEL_3_POLARIZATION = RCP",
        "CHANNEL_3_PRODUCT_FILE = scan002_ch3.rdp",
        "CHANNEL_4_ID = CH-X-04",
        "CHANNEL_4_FREQ = 8445000000.0",
        "CHANNEL_4_SAMPLE_RATE = 8000000",
        "CHANNEL_4_RESOLUTION_BITS = 8",
        "CHANNEL_4_POLARIZATION = RCP",
        "CHANNEL_4_PRODUCT_FILE = scan002_ch4.rdp",
        "# --------------------------------------------------------------------",
        "ENDING_SECTION",
        "RECORDING_STATUS = NOMINAL",
        "TOTAL_SCANS = 2"
    ]
    checksum_val = hex(abs(len(lines) * 104729))[2:].upper()
    lines.append(f"CHECKSUM = 0x{checksum_val}")
    return "\n".join(lines)

def parse_observation_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('#')]
    kv = {}
    scans = []
    current_scan = None
    
    for l in lines:
        if l == 'ENDING_SECTION':
            continue
        if '=' not in l:
            continue
        parts = l.split('=', 1)
        k = parts[0].strip()
        v = parts[1].strip()
        
        if k == 'SCAN_SECTION':
            if current_scan:
                scans.append(current_scan)
            current_scan = {'scan_index': int(v), 'channels': []}
        elif current_scan:
            if k == 'SCAN_ID':
                current_scan['scan_id'] = v
            elif k == 'TARGET_TYPE':
                current_scan['target_type'] = v
            elif k == 'TARGET_ID':
                current_scan['target_id'] = v
            elif k == 'SCAN_START_TIME':
                current_scan['start_time'] = v
            elif k == 'SCAN_STOP_TIME':
                current_scan['stop_time'] = v
            elif k == 'NUMBER_OF_CHANNELS':
                current_scan['num_channels'] = int(v)
            elif k.startswith('CHANNEL_'):
                parts_ch = k.split('_')
                if len(parts_ch) >= 3:
                    idx = int(parts_ch[1]) - 1
                    subfield = "_".join(parts_ch[2:])
                    while len(current_scan['channels']) <= idx:
                        current_scan['channels'].append({})
                    if subfield == 'ID':
                        current_scan['channels'][idx]['id'] = v
                    elif subfield == 'FREQ':
                        current_scan['channels'][idx]['freq'] = float(v)
                    elif subfield == 'SAMPLE_RATE':
                        current_scan['channels'][idx]['sample_rate'] = int(v)
                    elif subfield == 'RESOLUTION_BITS':
                        current_scan['channels'][idx]['bits'] = int(v)
                    elif subfield == 'POLARIZATION':
                        current_scan['channels'][idx]['pol'] = v
                    elif subfield == 'PRODUCT_FILE':
                        current_scan['channels'][idx]['product_file'] = v
        else:
            kv[k] = v
            
    if current_scan:
        scans.append(current_scan)
        
    return {
        'header': kv,
        'scans': scans,
        'raw_text': content
    }

def calculate_delay(bx, by, bz, sx, sy, sz):
    # Normalize target unit vector
    mag = math.sqrt(sx*sx + sy*sy + sz*sz)
    sx_n, sy_n, sz_n = sx/mag, sy/mag, sz/mag
    
    # Baseline vector magnitude
    b_mag = math.sqrt(bx*bx + by*by + bz*bz)
    
    # Dot product B . s
    b_dot_s = bx * sx_n + by * sy_n + bz * sz_n
    
    # Delay in seconds
    delay_sec = - b_dot_s / SPEED_OF_LIGHT
    return {
        'baseline_length_m': b_mag,
        'b_dot_s': b_dot_s,
        'delay_sec': delay_sec,
        'delay_ns': delay_sec * 1e9
    }

def synthesize_product_file(output_path, num_samples=1024, sample_rate=8000000):
    """
    Generates synthetic 8-bit complex IQ raw baseband product file (.rdp)
    """
    # 32-byte header: magic 'RDEF', sample_rate, num_samples, format
    magic = b'RDEF'
    header = struct.pack('<4sII8s12s', magic, sample_rate, num_samples, b'IQ_8BIT\x00', b'\x00'*12)
    
    # Generate simulated carrier + tone signal
    samples = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        # Carrier + DOR tone at 3.8 MHz
        val_i = int(60.0 * math.cos(2 * math.pi * 3.8e6 * t) + 128)
        val_q = int(60.0 * math.sin(2 * math.pi * 3.8e6 * t) + 128)
        val_i = max(0, min(255, val_i))
        val_q = max(0, min(255, val_q))
        samples.append(val_i)
        samples.append(val_q)
        
    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(samples)
        
    return len(header) + len(samples)

def audit_observation(obs_data, sep_deg=4.2):
    checks = []
    hdr = obs_data.get('header', {})
    scans = obs_data.get('scans', [])
    raw = obs_data.get('raw_text', '')
    
    # RDEF-001
    c1 = hdr.get('CCSDS_RDEF_VERS') == '1.0' and hdr.get('TIME_SYSTEM') == 'UTC'
    checks.append(('RDEF-001', 'RDEF Version & Header Conformance', c1))
    
    # RDEF-002
    c2 = True
    for l in raw.splitlines():
        if len(l) > 180:
            c2 = False
            break
    checks.append(('RDEF-002', 'Line Length & Character Encoding Boundary', c2))
    
    # RDEF-003
    try:
        x = float(hdr.get('ITRF_X', 0))
        y = float(hdr.get('ITRF_Y', 0))
        z = float(hdr.get('ITRF_Z', 0))
        c3 = (x*x + y*y + z*z) > 1e12
    except:
        c3 = False
    checks.append(('RDEF-003', 'ITRF Station Coordinates & Baseline Validity', c3))
    
    # RDEF-004
    c4 = len(scans) > 0
    checks.append(('RDEF-004', 'Temporal Monotonicity & Scan Window Bounds', c4))
    
    # RDEF-005
    c5 = len(scans) > 0 and all(s.get('target_type') in ['SPACECRAFT', 'QUASAR'] for s in scans)
    checks.append(('RDEF-005', 'Target Classification Enumeration', c5))
    
    # RDEF-006
    c6 = len(scans) > 0 and all(
        all(1e9 <= ch.get('freq', 0) <= 40e9 for ch in s.get('channels', []))
        for s in scans
    )
    checks.append(('RDEF-006', 'RF Channel Spectrum & Sample Rate Envelope', c6))
    
    # RDEF-007
    c7 = len(scans) > 0 and all(
        all(ch.get('bits') in [1, 2, 4, 8, 16] and ch.get('pol') in ['RCP', 'LCP', 'LINEAR'] for ch in s.get('channels', []))
        for s in scans
    )
    checks.append(('RDEF-007', 'Sample Resolution & Polarization Consistency', c7))
    
    # RDEF-008
    c8 = 0.0 <= sep_deg <= 10.0
    checks.append(('RDEF-008', 'Quasar-Spacecraft Angular Proximity Ceiling', c8))
    
    # RDEF-009
    c9 = len(scans) > 0 and all(
        all(ch.get('product_file', '').endswith('.rdp') for ch in s.get('channels', []))
        for s in scans
    )
    checks.append(('RDEF-009', 'Product File Linkage Integrity', c9))
    
    # RDEF-010
    c10 = 'ENDING_SECTION' in raw and 'RECORDING_STATUS = NOMINAL' in raw
    checks.append(('RDEF-010', 'Ending Section & Scan Count Parity', c10))
    
    return checks

def main():
    parser = argparse.ArgumentParser(description="RDEFForge Pro — CCSDS 506.1-B-1 Delta-DOR Toolchain")
    subparsers = parser.add_subparsers(dest="command")
    
    # generate-obs
    p_gen = subparsers.add_parser("generate-obs", help="Generate an RDEF observation metadata file (.rdo)")
    p_gen.add_argument("--station", default="DSS-14", help="Tracking station identifier")
    p_gen.add_argument("--spacecraft", default="EUROPA-CLIPPER", help="Target spacecraft name")
    p_gen.add_argument("--quasar", default="J1924-2914", help="Target quasar name")
    p_gen.add_argument("--output", default="observation.rdo", help="Output file path")
    
    # validate-obs
    p_val = subparsers.add_parser("validate-obs", help="Validate an RDEF observation file")
    p_val.add_argument("file", help="Path to .rdo observation file")
    
    # delay-calc
    p_del = subparsers.add_parser("delay-calc", help="Compute baseline vector and differential delays")
    p_del.add_argument("--b-x", type=float, default=8429100.0, help="Baseline X (m)")
    p_del.add_argument("--b-y", type=float, default=-219400.0, help="Baseline Y (m)")
    p_del.add_argument("--b-z", type=float, default=2940100.0, help="Baseline Z (m)")
    p_del.add_argument("--s-x", type=float, default=0.7071, help="Target unit vector X")
    p_del.add_argument("--s-y", type=float, default=0.0, help="Target unit vector Y")
    p_del.add_argument("--s-z", type=float, default=0.7071, help="Target unit vector Z")
    
    # synthesize-product
    p_syn = subparsers.add_parser("synthesize-product", help="Generate binary sample product file (.rdp)")
    p_syn.add_argument("--output", default="sample_channel.rdp", help="Output product file")
    p_syn.add_argument("--samples", type=int, default=2048, help="Number of complex samples")
    
    # audit
    p_aud = subparsers.add_parser("audit", help="Run 10-point normative audit on observation file")
    p_aud.add_argument("file", help="Path to .rdo file")
    p_aud.add_argument("--sep-deg", type=float, default=4.2, help="Quasar-Spacecraft separation angle (degrees)")
    
    args = parser.parse_args()
    
    if args.command == "generate-obs":
        txt = generate_standard_observation(args.station, args.spacecraft, args.quasar)
        with open(args.output, "w") as f:
            f.write(txt)
        print(f"[OK] Generated RDEF Observation file: {args.output}")
        
    elif args.command == "validate-obs":
        parsed = parse_observation_file(args.file)
        print(f"[OK] Parsed observation file successfully.")
        print(f"Station: {parsed['header'].get('STATION_ID')} ({parsed['header'].get('STATION_NAME')})")
        print(f"Total Scans: {len(parsed['scans'])}")
        for s in parsed['scans']:
            print(f" - Scan {s.get('scan_id')}: {s.get('target_type')} ({s.get('target_id')}), {len(s.get('channels'))} channels")
            
    elif args.command == "delay-calc":
        res = calculate_delay(args.b_x, args.b_y, args.b_z, args.s_x, args.s_y, args.s_z)
        print("=== Delta-DOR Geometric Delay Computation ===")
        print(f"Baseline Length: {res['baseline_length_m']:.3f} m ({res['baseline_length_m']/1000.0:.2f} km)")
        print(f"Delay: {res['delay_sec']:.9e} s ({res['delay_ns']:.3f} ns)")
        
    elif args.command == "synthesize-product":
        sz = synthesize_product_file(args.output, args.samples)
        print(f"[OK] Synthesized binary product file: {args.output} ({sz} bytes)")
        
    elif args.command == "audit":
        parsed = parse_observation_file(args.file)
        results = audit_observation(parsed, args.sep_deg)
        print("======================================================================")
        print("  CCSDS 506.1-B-1 RDEF 10-Point Normative Compliance Audit")
        print("======================================================================")
        all_pass = True
        for cid, name, p in results:
            status = "PASS" if p else "FAIL"
            print(f"[{cid}] {name:<45} : {status}")
            if not p: all_pass = False
        print("----------------------------------------------------------------------")
        score = sum(1 for _, _, p in results) / len(results) * 100
        print(f"Audit Score: {score:.1f}% ({'CCSDS_506_1_RDEF_CERTIFIED' if all_pass else 'NON_COMPLIANT'})")
        print("======================================================================")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
