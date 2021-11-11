import sys, getopt
from src.VideoGenerator import VideoGenerator
from src.TestSuite import TestSuite

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"hl:g:t",["layout=","ghost="])
    except getopt.GetoptError:
      print("Incorrect format: main.py -h for info")
      sys.exit(2)

    layout = None
    ghost = None
    test_suite = False
    for opt, arg in opts:
        if opt == "-h":
            print("""\t    -h\t show command usage
            -l | --layout <layout>\t specify the layout to be used
            -g | --ghost <ghostfile>\t specify the ghost file to be read
            -t\t run the test suite to preview the layout\n
            example usage:
            main.py -l layout1 -g ghost.rkg OR
            main.py -l layout1 -t""")
            sys.exit(2)

        elif opt in ("-l", "--layout"):
            layout = arg
        elif opt in ("-g", "--ghost"):
            ghost = arg
        elif opt == "-t":
            test_suite = True

    if layout is None:
        print("No layout specified: main.py -h for info")
        sys.exit(2)

    if test_suite:
        t = TestSuite(layout)
        t.start_loop()
    else:
        if ghost is None:
            print("No ghost file specified: main.py -h for info")
            sys.exit(2)
        f = VideoGenerator(layout, ghost)
        f.run()


if __name__ == "__main__":
   main(sys.argv[1:])