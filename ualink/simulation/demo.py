from ualink.simulation.end_to_end import simulate_read
from ualink.system.accelerator import Accelerator

def main():
    a1 = Accelerator(1)
    a2 = Accelerator(2)
    a1.connect_port(0, 2)
    a2.connect_port(0, 1)
    simulate_read(a1, a2)
    print("Demo ran.")

if __name__ == "__main__":
    main()
