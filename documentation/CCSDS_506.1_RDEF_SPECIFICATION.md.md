# CCSDS 506.1-B-1 Delta-DOR Raw Data Exchange Format (RDEF) Specification

## Technical Reference, Mathematical Foundations & Correlation Data Models

### 1\. Executive Summary & Purpose

The **Delta-Differential One-Way Ranging (Delta-DOR)** technique is the international gold standard for deep-space interplanetary spacecraft navigation. Defined by the Consultative Committee for Space Data Systems (CCSDS) under **CCSDS 506.1-B-1 (Blue Book, Issue 1\)**, the **Delta-DOR Raw Data Exchange Format (RDEF)** specifies the standard data interchange structures required for cross-support observations between space agencies—including NASA (Deep Space Network \- DSN), ESA (ESTRACK), JAXA, ISRO, and commercial ground station networks.

Delta-DOR delivers sub-nanoradian angular position determination (\~1 nrad \$\\approx 0.2\$ milliarcseconds), enabling precision orbit insertion for missions to Mars, Jupiter, asteroids, and the Moon.

---

### 2\. Delta-DOR Mathematical Principles

#### 2.1 Interferometric Baseline Geometry

Two widely separated tracking stations (Station 1 and Station 2\) with geocentric position vectors \$\\vec{R}\_1\$ and \$\\vec{R}\_2\$ in the International Terrestrial Reference Frame (ITRF) form a baseline vector \$\\vec{B}\$:

\$\$\\vec{B} \= \\vec{R}\_2 \- \\vec{R}\_1 \= \[X\_2 \- X\_1, Y\_2 \- Y\_1, Z\_2 \- Z\_1\]^T\$\$

The length of the intercontinental baseline \$D\_B\$ is:

\$\$D\_B \= \|\\vec{B}\| \= \\sqrt{(X\_2 \- X\_1)^2 \+ (Y\_2 \- Y\_1)^2 \+ (Z\_2 \- Z\_1)^2}\$\$

For DSN intercontinental baselines (Goldstone–Madrid, Goldstone–Canberra, Madrid–Canberra), \$D\_B \\approx 8,400\\text{ km}\$ to \$10,600\\text{ km}\$.

#### 2.2 Geometric Delay Formulation

For a target located along unit vector \$\\vec{s}\$, the wavefront arrival time difference (geometric delay \$\\tau\_g\$) is:

\$\$\\tau\_g \= \-\\frac{\\vec{B} \\cdot \\vec{s}}{c}\$\$

where \$c \= 299,792,458\\text{ m/s}\$ is the speed of light in vacuum.

#### 2.3 Clock Drift & Atmospheric Error Cancellation

The actual observed delay \$\\tau\_{\\text{obs}}\$ contains instrument clock biases and propagation media delays:

\$\$\\tau\_{\\text{obs}} \= \\tau\_g \+ \\Delta\\tau\_{\\text{clock}} \+ \\Delta\\tau\_{\\text{troposphere}} \+ \\Delta\\tau\_{\\text{ionosphere}} \+ \\epsilon\$\$

By observing a natural extragalactic radio source (quasar) with precisely known celestial coordinates (from the International Celestial Reference Frame \- ICRF) in close angular proximity (\$\\theta \\le 10^\\circ\$, ideally \$\\le 6^\\circ\$) within minutes of the spacecraft observation:

\$\$\\Delta\\tau \= \\tau\_{\\text{obs, SC}} \- \\tau\_{\\text{obs, Quasar}} \\approx \\tau\_{g, \\text{SC}} \- \\tau\_{g, \\text{Quasar}}\$\$

Because both signals traverse nearly identical ray paths through the atmosphere and share the same station frequency standards, common clock offsets and atmospheric delays cancel out to sub-nanosecond accuracy.

#### 2.4 Angular Offset Determination

The angular position offset \$\\Delta\\theta\$ perpendicular to the baseline is given by:

\$\$\\Delta\\theta \= \\frac{c \\cdot \\Delta\\tau}{D\_B \\cdot \\cos(\\alpha)}\$\$

where \$\\alpha\$ is the elevation angle relative to the baseline normal. With \$\\Delta\\tau\$ resolved to \$\\approx 0.05\\text{ ns}\$ across an \$8,000\\text{ km}\$ baseline, angular resolution reaches \$\\approx 1.8\\times 10^{-9}\\text{ rad}\$ (\$0.37\\text{ mas}\$).

---

### 3\. RDEF File Architecture

CCSDS 506.1-B-1 defines a dual-file hierarchy:

#### 3.1 Observation File (`.rdo` / ASCII Text Metadata)

Contains parameters describing the tracking session, station coordinates, targets, scan sections, and channel parameters.

- **Header Section**: Mandatory version (`CCSDS_RDEF_VERS = 1.0`), creation date, originator, station IDs, ITRF coordinates, time system (`UTC`), and observation duration.  
- **Scan Sections**: One or more scans covering alternating targets (`QUASAR` \$\\rightarrow\$ `SPACECRAFT` \$\\rightarrow\$ `QUASAR`).  
- **Channel Specifications**: Intermediate frequency (IF), sample rate (e.g., 2, 4, 8, 16 MSamples/s), resolution bits (1, 2, 4, 8, 16 bits/sample), polarization (`RCP`, `LCP`), and linkage to raw product files.  
- **Ending Section**: Status (`NOMINAL`), scan count verification, and checksum.

#### 3.2 Product File (`.rdp` / Raw Baseband Binary Stream)

Contains digitized, filtered, downconverted complex (I/Q) baseband samples recorded during each scan for a single frequency channel.

- Structured with a standardized 32-byte binary header (`RDEF` magic word, sample rate, sample count, sample format).  
- Followed by contiguous time-ordered sample words.

---

### 4\. Implementation Guidelines

1. **Station Identifiers**: Must conform to SANA Ground Station Registries (e.g., `DSS-14`, `DSS-43`, `DSS-63`, `CEBREROS`, `NEW_NORCIA`).  
2. **Frequency Bands**:  
   - S-band: 2.2 GHz – 2.3 GHz  
   - X-band: 8.4 GHz – 8.5 GHz  
   - Ka-band: 31.8 GHz – 32.3 GHz  
3. **Quasar Catalog**: Quasars must be referenced from ICRF3 (International Celestial Reference Frame 3\) with source position uncertainties \$\< 0.25\\text{ mas}\$.