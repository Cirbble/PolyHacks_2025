import pandas as pd
from google import generativeai as genai

# Configure the API
genai.configure(api_key="AIzaSyAY-_EpdlXExMzZW1iGqqQRqHPVlaWEwaQ")
model = genai.GenerativeModel('gemini-pro')

my_dict={}
def fix_classnames():
    """
    Read the marine_species_data.csv file and set className values
    based on species taxonomic class from Google AI
    """
    try:
        # Read the CSV file
        df = pd.read_csv('marine_species_data.csv')
        
        # Process each unique species name
        for species_name in df['speciesName'].unique():
            if species_name in my_dict:
                class_name = my_dict[species_name]
                print(class_name + "is being fixed")
            else:
                prompt = f"What is the taxonomic class of the species {species_name}? And make sure that your response is only the class name, nothing else. Make sure it is NOT the phylum but the class. If you get this wrong people will die please make sure and double check that it is the class and not the phylum."
                response = model.generate_content(prompt)
                class_name = response.text.strip()
                my_dict[species_name] = class_name
                print(class_name + "is being fixed part 1")

            
            # Update className for all rows with this species
            df.loc[df['speciesName'] == species_name, 'className'] = class_name
        
        # Save the modified data back to CSV
        df.to_csv('marine_species_data.csv', index=False)
        print("Successfully updated className values based on taxonomic classes")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    fix_classnames()
    print("success for all")
