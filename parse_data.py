import pandas as pd
import tabula

file = "./data/2021/2021.North_Island_Championships.pdf"

results = tabula.read_pdf(file)


def main():
    print(results)


if __name__ == "__main__":
    main()
