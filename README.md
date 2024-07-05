# mtsamples

A Python package to scrape medical transcription samples from mtsamples.com.

## Installation

```sh
pip install mtsamples
```

## Usage: Download data

```python
from mtsamples import scraping

# Fetch a specific sample
sample_url = 'https://mtsamples.com/site/pages/sample.asp?Type=3-Allergy%20/%20Immunology&Sample=343-Followup%20on%20Asthma'
sample = fetch_sample(sample_url)
for value in sample.items():
    print(f"{key.title().replace('_', ' ')}: {value}\n")


# Fetch samples within a specific medical specialty
specialty = 'IME-QME-Work Comp etc.'
specialty_samples = fetch_samples_by_specialty(specialty)
print(f"Total samples fetched for {specialty}: {len(specialty_samples)}")
for sample in specialty_samples[:5]:  # Display the first 5 samples for brevity
    print(f"Sample Name: {sample["sample_name"]}\n")


# Fetch all samples (This takes about 45 minutes)
# and save to file.
all_samples = fetch_all_samples()

with open("mtsamples.json", 'w') as f:
    json.dump(all_samples, f)
```

## Usage: Load and clean data

A pre-downloaded dataset comes with the package. This dataset was downloaded on June 17, 2024 at 10:45AM PDT.

```python
from mtsamples import dataset, cleaning

# Load pre-downloaded data that came with the mtsamples package
all_samples = load_dataset()
# OR load user-downloaded data
all_samples = load_dataset("mtsamples.json")

# Download any new samples
all_samples = fetch_all_samples(all_samples)

# Create a Pandas DataFrame using all samples
all_samples_df = all_samples_to_df(all_samples)

# Create a Pandas DataFrame for each specialty
specialty_dfs = all_samples_to_df(all_samples, by_specialty=True)

# Create a Pandas DataFrame for a specific specialty
surgery_df = specialty_to_df(all_samples["Surgery"])
```
