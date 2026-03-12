import numpy as np


def cap_from_impedance(freq, Z):
    """Capacitor which equals Z impedance at freq."""
    omega = 2 * np.pi * freq
    return 1 / (omega * Z)


def ind_from_impedance(freq, Z):
    """Inductor which equals Z impedance at freq."""
    omega = 2 * np.pi * freq
    return Z / omega


def matched_Q(freq, R_s=50, R_p=50):
    """This matches the Q for impedance matching circuits.

    Keyword arguments:
    freq: frequency of interest (Hz)
    R_s: source resistance (Ohms, inline, default 50)
    R_p: load resistance (Ohms, grounded, default 50)

    Returns:
    X_s: inline impedance calculated for matching
    X_p: paralleled to load (grounded) impedance calculated for matching
    """
    Q_s = np.sqrt((R_p / R_s) - 1)  # Q_s = Q_p for matching impedance
    Q_p = np.sqrt((R_p / R_s) - 1)  # Q_s = Q_p for matching impedance

    X_s = Q_s * R_s
    X_p = R_p / Q_p
    return X_s, X_p


def print_schematic(freq, R_s, R_p, C_s, C_p, L_s, L_p):
    """Saves to current location a PDF and .sch file for both circuits."""
    try:
        from lcapy import Circuit

        print(f"Imported lcapy.")
        # Write to a new file called circuit.sch with the component values
        with open("circuit1.sch", "w", encoding="utf-8") as f:
            f.write(f"V1 1 0 ac; down=1.75, a_={freq / 1e3} kHz\n")
            f.write(f"Rs 1 2 {R_s}; right=1.75\n")
            f.write(f"Cs 2 3 {C_s}; right\n")
            f.write(f"W 0 5; right\n")
            f.write(f"Lp 3 5 {L_p}; down\n")
            f.write(f"W 3 3a; right=1.75\n")
            f.write(f"W 5 5a; right=0.75\n")
            f.write(f"Rl 3a 5a {R_p}; down\n")
            f.write(f"W 3a 3b; right=0.75\n")
            f.write(f"W 5a 5b; right=0.75\n")
            f.write(f"P2 3b 5b; down\n")
            f.write(f"; draw_nodes=connections, label_nodes=none, label_style=stacked")
        f.close()
        cct = Circuit("circuit1.sch")
        cct.draw("circuit1.pdf")
        # Write other way circuit can be
        with open("circuit2.sch", "w", encoding="utf-8") as f:
            f.write(f"V1 1 0 ac; down=1.75, a_={freq / 1e3} kHz\n")
            f.write(f"Rs 1 2 {R_s}; right=1.75\n")
            f.write(f"Ls 2 3 {L_s}; right\n")
            f.write(f"W 0 5; right\n")
            f.write(f"Cp 3 5 {C_p}; down\n")
            f.write(f"W 3 3a; right=1.75\n")
            f.write(f"W 5 5a; right=0.75\n")
            f.write(f"Rl 3a 5a {R_p}; down\n")
            f.write(f"W 3a 3b; right=0.75\n")
            f.write(f"W 5a 5b; right=0.75\n")
            f.write(f"P2 3b 5b; down\n")
            f.write(f"; draw_nodes=connections, label_nodes=none, label_style=stacked")
        f.close()
        cct = Circuit("circuit2.sch")
        cct.draw("circuit2.pdf")
    except ImportError:
        print(f"The module 'lcapy' is not installed.")
        print(f"You can install it using 'pip install lcapy' in your terminal.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="Impedance Matcher",
        description="Gives capacitor and inductor values necessary to match source and load impedances.",
        epilog="Prints values to stdout, and if user has lcapy module also saves PDF of schematic.",
    )
    parser.add_argument("Rs", help="Source impedance (Ohms)", type=float)
    parser.add_argument("Rl", help="Load impedance (Ohms)", type=float)
    parser.add_argument("freq", help="Frequency (Hz)", type=float)
    parser.add_argument("-r", "--range", action="store_true", help="frequency range")
    args = parser.parse_args()
    R_s = args.Rs
    R_p = args.Rl
    freq = args.freq

    if args.range:
        print("Input frequency range in Hz")
        start_freq = float(input("Start frequency: "))
        stop_freq = float(input("Stop frequency: "))
        freq_range = np.linspace(start_freq, stop_freq)
        X_s, X_p = matched_Q(freq_range, R_s, R_p)
        C_s, L_p = (
            cap_from_impedance(freq_range, X_s),
            ind_from_impedance(freq_range, X_p),
        )
        L_s, C_p = (
            ind_from_impedance(freq_range, X_s),
            cap_from_impedance(freq_range, X_p),
        )
        for i, element in enumerate(freq_range):
            print(f"{int(element)} Hz: C_s: {C_s[i]} F, \t L_p: {L_p[i]} H")
        print("Or")
        for i, element in enumerate(freq_range):
            print(f"{int(element)} Hz: L_s: {L_s[i]} H, \t C_p: {C_p[i]} F")
    else:
        X_s, X_p = matched_Q(freq, R_s, R_p)
        C_s, L_p = cap_from_impedance(freq, X_s), ind_from_impedance(freq, X_p)
        L_s, C_p = ind_from_impedance(freq, X_s), cap_from_impedance(freq, X_p)
        print(f"C_s: {C_s} F, \t L_p: {L_p} H")
        print("Or")
        print(f"L_s: {L_s} H, \t C_p: {C_p} F")

        print_schematic(freq, R_s, R_p, C_s, C_p, L_s, L_p)
