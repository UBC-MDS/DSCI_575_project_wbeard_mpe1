# Find Good Books Dashboard

## Table of Contents

- [About](#about)
- [Setup](#setup)
- [Our Data](#data)
- [Dashboard](#dashboard)

## About {#about}

This dashboard uses a **sample** of books from Amazon's millions of book reviews. The user will be able to search these books using two different types of search systems: key-word- and/or semantic-based.

**Github Repo:** <https://github.com/UBC-MDS/DSCI_575_project_wbeard_mpe1>

## Setup {#setup}

### 1) Download the repository

Clone the project repository and navigate to the root folder:

``` bash
git clone https://github.com/UBC-MDS/DSCI_575_project_wbeard_mpe1
cd DSCI_575_project_wbeard_mpe1
```

### 2) Create and activate the conda environment

From the repository root:

``` bash
conda env create -f environment.yml
conda activate find-good-books
```

**Note:** throughtout running this project, if you run into issues with importing `nltk`, additional downloads/updates may be required.

``` bash
nltk.download('punkt')
nltk.download('stopwords')
```

## Our Data {#data}

A sample from Amazon's "Books" reviews. Source: [Reviews and Meta Data](https://amazon-reviews-2023.github.io/)

**Note:** these are very large files. To prevent having every individual download them to run our project, we have pre-sampled data from both the "review" and "meta" datasets. The two results were then joined and turned into a parquet file: `data/processed/merged.parquet`. This was done locally and then pushed to the repository, providing ease of use for anyone running this project. If you would like to see how we did this, please read the instructions below.

### 1) Download the raw data

Follow the "Source" link above and download both files for the "Books" category. Unzip the files and place in the `data/raw` folder of this project, locally.

### 2) Generate sample data

To generate a sample of books, their reviews, and merge them into a single parquet file:

``` bash
python src/get_data_sample.py
```

### 3) Regenerate search systems

Since this changes the sample book data, both the key-word and semantic search systems need to be updated to reflect what is now in this parquet file:

``` bash
python src/search-systems.py
```

## Dashboard {#dashboard}

Our dashboard is a Shiny for Python app. Currently, our repository is set to private which prevents it from being hosted on Posit Connect Cloud. To run our app and interact with it, please make sure you have followed the [Setup](#setup) instructions and ensure you have the correct environment activated. Once you have done that, proceed.

### 1) Navigate to the project root directory

Run the following command in your terminal. Copy and paste the local URL [**http://127.0.0.1:8000**](http://127.0.0.1:8000){.uri} into your browser to connect.

``` bash
shiny run --reload app/app.py
```

### 2. With our app open

Enter your search query into the input field and select the search type you would like to use. The generated results are those top-ranked-books based on our data sample.

### Demo

![Here is a demo of the dashboard:](img/demo.gif)

## License

MIT

### Main Contributors

- Michael Eirikson
- Wesley Beard
