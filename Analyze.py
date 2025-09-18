import subprocess
import os
import matplotlib.pyplot as plt
import tempfile

# XFOIL path (next to script)
XFOIL_PATH = os.path.join(os.path.dirname(__file__), "xfoil.exe")

def run_xfoil(airfoil="2412", alphas=[0, 2, 4, 6, 8, 10], Re=1e6, Mach=0.0):
    polar_file = os.path.abspath("polar_temp.txt")
    
    commands = [
        f"NACA {airfoil}\n",
        "PANE\n",
        "OPER\n",
        f"VISC {Re}\n",
        f"MACH {Mach}\n",
        "ITER 100\n",
        "PACC\n",
        f"{polar_file}\n",
        "\n"
    ]
    
    for alpha in alphas:
        commands.append(f"ALFA {alpha}\n")
    
    commands.append("QUIT\n")

    try:
        process = subprocess.Popen(
            [XFOIL_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(''.join(commands))

        if stderr:
            print("XFOIL Error:", stderr)

        polar_data_list = []
        if os.path.exists(polar_file):
            with open(polar_file, "r") as f:
                lines = f.readlines()
                for line in lines[12:]:
                    parts = line.split()
                    if len(parts) >= 6:
                        polar_data_list.append({
                            "alpha": float(parts[0]),
                            "Cl": float(parts[1]),
                            "Cd": float(parts[2]),
                            "Cm": float(parts[4])
                        })
            os.remove(polar_file)
        else:
            print(f"Polar file not found for airfoil {airfoil}.")
        return polar_data_list

    except FileNotFoundError:
        print(f"Error: XFOIL not found at {XFOIL_PATH}")
        return None

def get_airfoil_coords(airfoil="2412"):
    airfoil_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt').name
    commands = [
        f"NACA {airfoil}\n",
        "PANE\n",
        f"SAVE {airfoil_file}\n",
        "QUIT\n"
    ]

    try:
        process = subprocess.Popen(
            [XFOIL_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(''.join(commands))
        if stderr:
            print(f"XFOIL Error (airfoil shape {airfoil}):", stderr)

        xs, ys = [], []
        with open(airfoil_file, "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) >= 2:
                    xs.append(float(parts[0]))
                    ys.append(float(parts[1]))
        return xs, ys

    finally:
        if os.path.exists(airfoil_file):
            os.remove(airfoil_file)

def plot_airfoil_and_polar(xs, ys, polar_data, airfoil_name):
    if not polar_data:
        print(f"No polar data to plot for {airfoil_name}.")
        return

    alphas = [p['alpha'] for p in polar_data]
    Cls = [p['Cl'] for p in polar_data]
    Cds = [p['Cd'] for p in polar_data]
    Cms = [p['Cm'] for p in polar_data]
    ClCd = [cl/cd if cd != 0 else 0 for cl, cd in zip(Cls, Cds)]

    fig, axs = plt.subplots(5, 1, figsize=(10, 12))
    
    # Airfoil shape
    axs[0].plot(xs, ys, '-o', markersize=2)
    axs[0].set_aspect('equal', 'box')
    axs[0].set_title(f"NACA Airfoil {airfoil_name}")
    axs[0].set_xlabel("x/c")
    axs[0].set_ylabel("y/c")
    axs[0].grid(True)

    # Coefficient of Lift
    axs[1].plot(alphas, Cls, '-o', color='b')
    axs[1].set_ylabel('Cl')
    axs[1].grid(True)

    # Coefficient of Drag
    axs[2].plot(alphas, Cds, '-s', color='r')
    axs[2].set_ylabel('Cd')
    axs[2].grid(True)

    # Pitching Moment Coefficient
    axs[3].plot(alphas, Cms, '-^', color='g')
    axs[3].set_ylabel('Cm')
    axs[3].grid(True)

    # Lift to Drag Coefficient
    axs[4].plot(alphas, ClCd, '-d', color='m')
    axs[4].set_xlabel('Alpha (deg)')
    axs[4].set_ylabel('Cl/Cd')
    axs[4].grid(True)

    plt.tight_layout()
    plt.show()


airfoils = ["2412", "0012", "4412"]  
alphas = list(range(0, 16, 2))       

for airfoil in airfoils:
    print(f"Analyzing NACA {airfoil}...")
    polar_list = run_xfoil(airfoil, alphas=alphas)
    xs, ys = get_airfoil_coords(airfoil)
    plot_airfoil_and_polar(xs, ys, polar_list, airfoil)

