# Parsing the Competition Results

This code includes code used to turn pdf and excel files into code that is readable by [lifter-api](https://github.com/ChrisrchurchCityWeightlifting/lifter-api)

## Requirements

- AWS SDK and credentials
- Jupyter set up
- Python 3.10
- `lifter-api-wrapper` (I'm using `pipenv` instead of `conda`)

## How This Works

PDF files aren't easy to deal with. I could use `tabula-py`but I didn't want to install Java or use a docker container. So I'm using OCR!

The process:

1. Upload PDF to AWS S3 Bucket
2. From there, AWS Textract reads the PDF and sends tabular information as a JSON
3. Breakdown the JSON file
4. Utilise lower level functions of `lifter-api-wrapper` to build higher level functions to turn JSON data into information the API can ingest
5. Store information on database
6. Repeat this for other PDF documents
7. Flex!

## Structure of Project

```
.
├── ...
└── data
    ├── ...
    └── 2022
        └── 2022 NZ International
            ├── 2022.NZ_International.pdf
            └── parsing.ipynb # <=== CODE IS HERE

```

## Contributions

I'm all alone!
