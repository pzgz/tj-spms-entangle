""" Main application entry point.

    python -m entangle  ...

"""

# print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(
#     __file__, __name__, str(__package__)))

from .cli import main as gate

def main():
    """ Execute the application.

    """
    # raise NotImplementedError
    gate()


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
