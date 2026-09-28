# ============================================
# FILE: transform.py (PATH FIXED VERSION)
# PURPOSE: Complete feature engineering for distributed analytics
# ============================================

import pandas as pd
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to DCDAS folder, then to datasets/processed
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # This is DCDAS folder

INPUT_PATH = os.path.join(BASE_DIR, "datasets", "processed", "CRIME_DATA_CLEANED.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "datasets", "processed", "CRIME_DATA_TRANSFORMED.csv")

print(f"📁 Script location: {SCRIPT_DIR}")
print(f"📁 Base directory: {BASE_DIR}")
print(f"📖 Looking for input: {INPUT_PATH}")

# Crime Severity Mapping (1-10 scale, 10 = most severe)
SEVERITY_MAP = {
    'Violence and sexual offences': 10,
    'Possession of weapons': 9,
    'Drugs': 8,
    'Burglary': 7,
    'Robbery': 7,
    'Criminal damage and arson': 5,
    'Vehicle crime': 5,
    'Other theft': 4,
    'Theft from the person': 4,
    'Public order': 3,
    'Shoplifting': 2,
    'Bicycle theft': 2,
    'Other crime': 4,
}

# Crime Category Grouping
CRIME_CATEGORY = {
    'Violence and sexual offences': 'Violent Crime',
    'Possession of weapons': 'Violent Crime',
    'Robbery': 'Violent Crime',
    'Burglary': 'Property Crime',
    'Vehicle crime': 'Property Crime',
    'Shoplifting': 'Property Crime',
    'Bicycle theft': 'Property Crime',
    'Other theft': 'Property Crime',
    'Theft from the person': 'Property Crime',
    'Criminal damage and arson': 'Property Crime',
    'Drugs': 'Drug Related',
    'Public order': 'Public Order',
    'Other crime': 'Other',
}

try:
    # Check if file exists
    if not os.path.exists(INPUT_PATH):
        print(f"❌ ERROR: Input file not found at: {INPUT_PATH}")
        print("   Please make sure CRIME_DATA_CLEANED.csv exists in datasets/processed/")
        exit(1)
    
    df = pd.read_csv(INPUT_PATH)
    print(f"📖 Loaded {len(df)} records from {INPUT_PATH}")
    print("🔄 Starting Feature Engineering...")

    # ============================================
    # 1. DATE TRANSFORMATION (For Trends)
    # ============================================
    df[['Year', 'Month_Num']] = df['Month'].str.split('-', expand=True)
    
    month_map = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', 
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', 
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    df['Month_Name'] = df['Month_Num'].map(month_map)
    df['Year_Month'] = df['Year'] + '-' + df['Month_Num']
    print("✓ Date transformation complete")

    # ============================================
    # 2. TEXT STANDARDIZATION
    # ============================================
    df['Crime type'] = df['Crime type'].str.strip()
    df['Location'] = df['Location'].str.strip()
    df['LSOA name'] = df['LSOA name'].fillna('Unknown').str.strip()
    print("✓ Text standardization complete")

    # ============================================
    # 3. EXTRACT CLEAN AREA NAME
    # ============================================
    df['Area_Name'] = df['Location'].str.replace('On or near ', '', regex=False)
    df['Area_Name'] = df['Area_Name'].str.replace('On or near', '', regex=False)
    df['Area_Name'] = df['Area_Name'].str.strip()
    df.loc[df['Area_Name'] == '', 'Area_Name'] = df['LSOA name']
    print("✓ Area extraction complete")

    # ============================================
    # 4. CRIME SEVERITY SCORE
    # ============================================
    df['Severity_Score'] = df['Crime type'].map(SEVERITY_MAP).fillna(4)
    print("✓ Severity scoring complete")

    # ============================================
    # 5. CRIME CATEGORY GROUPING
    # ============================================
    df['Crime_Category'] = df['Crime type'].map(CRIME_CATEGORY).fillna('Other')
    print("✓ Crime categorization complete")

    # ============================================
    # 6. POLICE FORCE EXTRACTION
    # ============================================
    df['Police_Force'] = df['Reported by'].str.replace(' Constabulary', '', regex=False)
    df['Police_Force'] = df['Police_Force'].str.strip()
    print("✓ Police force extraction complete")

    # ============================================
    # 7. LOCATION TYPE CATEGORIZATION
    # ============================================
    def categorize_location(loc):
        loc_lower = str(loc).lower()
        if 'supermarket' in loc_lower:
            return 'Supermarket'
        elif 'parking' in loc_lower or 'car park' in loc_lower:
            return 'Parking Area'
        elif 'shopping' in loc_lower or 'retail' in loc_lower:
            return 'Shopping Area'
        elif 'nightclub' in loc_lower or 'bar' in loc_lower:
            return 'Nightlife'
        elif 'school' in loc_lower or 'college' in loc_lower:
            return 'Educational'
        elif 'hospital' in loc_lower:
            return 'Hospital'
        elif 'station' in loc_lower or 'railway' in loc_lower:
            return 'Transport Hub'
        elif 'park' in loc_lower or 'playing field' in loc_lower:
            return 'Park/Open Space'
        else:
            return 'Street/Residential'
    
    df['Location_Type'] = df['Location'].apply(categorize_location)
    print("✓ Location categorization complete")

    # ============================================
    # 8. CREATE SEASON COLUMN
    # ============================================
    season_map = {
        '01': 'Winter', '02': 'Winter', '03': 'Spring',
        '04': 'Spring', '05': 'Spring', '06': 'Summer',
        '07': 'Summer', '08': 'Summer', '09': 'Fall',
        '10': 'Fall', '11': 'Fall', '12': 'Winter'
    }
    df['Season'] = df['Month_Num'].map(season_map)
    print("✓ Season extraction complete")

    # ============================================
    # 9. OUTCOME SIMPLIFICATION
    # ============================================
    def simplify_outcome(outcome):
        if pd.isna(outcome):
            return 'Unknown'
        outcome_lower = str(outcome).lower()
        if 'unable to prosecute' in outcome_lower:
            return 'Unable to Prosecute'
        elif 'investigation complete' in outcome_lower and 'no suspect' in outcome_lower:
            return 'No Suspect Found'
        elif 'caution' in outcome_lower:
            return 'Caution Issued'
        elif 'court' in outcome_lower:
            return 'Court Action'
        elif 'charged' in outcome_lower:
            return 'Charged'
        elif 'local resolution' in outcome_lower:
            return 'Local Resolution'
        elif 'under investigation' in outcome_lower:
            return 'Under Investigation'
        else:
            return 'Other Outcome'
    
    df['Outcome_Simplified'] = df['Last outcome category'].apply(simplify_outcome)
    print("✓ Outcome simplification complete")

    # ============================================
    # 10. COORDINATE GROUPS
    # ============================================
    df['Lat_Group'] = df['Latitude'].round(2)
    df['Lon_Group'] = df['Longitude'].round(2)
    print("✓ Coordinate grouping complete")

    # ============================================
    # SAVE TRANSFORMED DATASET
    # ============================================
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "="*50)
    print("✅ TRANSFORMATION COMPLETE!")
    print("="*50)
    print(f"📁 Saved at: {OUTPUT_PATH}")
    print(f"📊 Total Records: {len(df)}")
    print(f"📋 Total Columns: {len(df.columns)}")
    print("\n🆕 New Columns Added:")
    new_cols = ['Year', 'Month_Num', 'Month_Name', 'Year_Month', 'Area_Name', 
                'Severity_Score', 'Crime_Category', 'Police_Force', 'Location_Type',
                'Season', 'Outcome_Simplified', 'Lat_Group', 'Lon_Group']
    for col in new_cols:
        print(f"   → {col}")
    print("="*50)

except Exception as e:
    print(f"❌ Error in Transformation: {e}")
    import traceback
    traceback.print_exc()