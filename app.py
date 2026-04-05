import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Medicare Part D Drug Map", layout="wide")
st.title("Medicare Part D Prescribing Map (2023)")
st.caption("State-level prescribing rates normalized by Part D enrollment. Data source: CMS Medicare Part D Prescribers by Geography and Drug, 2023.")

# ── Database connection ───────────────────────────────────────────────────────
DB_PATH = "database/cms.db"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# ── Drug list (cached) ────────────────────────────────────────────────────────
@st.cache_data
def load_drug_list():
    return pd.read_sql_query("""
        SELECT DISTINCT Gnrc_Name
        FROM part_d_geo
        WHERE Prscrbr_Geo_Lvl = 'State'
        GROUP BY Gnrc_Name
        HAVING COUNT(DISTINCT Prscrbr_Geo_Desc) >= 40
        ORDER BY Gnrc_Name
    """, conn)["Gnrc_Name"].tolist()

drug_list = load_drug_list()

# ── Therapeutic category map ──────────────────────────────────────────────────
CATEGORIES = {
    "Oncology": [
        "Lenalidomide", "Ibrutinib", "Palbociclib", "Venetoclax", "Pomalidomide",
        "Osimertinib Mesylate", "Abemaciclib", "Olaparib", "Ribociclib Succinate",
        "Alectinib Hcl", "Niraparib Tosylate", "Imatinib Mesylate", "Dasatinib",
        "Nilotinib Hcl", "Bosutinib", "Ponatinib Hcl", "Sunitinib Malate",
        "Sorafenib Tosylate", "Everolimus", "Erlotinib Hcl", "Gefitinib",
        "Crizotinib", "Axitinib", "Cabozantinib S-Malate", "Regorafenib",
        "Pazopanib Hcl", "Lapatinib Ditosylate", "Afatinib Dimaleate",
        "Ruxolitinib Phosphate", "Temozolomide", "Capecitabine", "Fluorouracil",
        "Hydroxyurea", "Mercaptopurine", "Cyclophosphamide", "Thalidomide",
        "Bicalutamide", "Enzalutamide", "Abiraterone Acetate", "Apalutamide",
        "Darolutamide", "Relugolix", "Tamoxifen Citrate", "Letrozole",
        "Anastrozole", "Exemestane", "Fulvestrant", "Ribociclib Succinate/Letrozole",
        "Venetoclax", "Selinexor", "Ixazomib Citrate", "Eltrombopag Olamine",
        "Rucaparib Camsylate", "Tucatinib", "Alpelisib", "Encorafenib",
        "Binimetinib", "Trametinib Dimethyl Sulfoxide", "Dabrafenib Mesylate",
        "Vismodegib", "Trifluridine/Tipiracil Hcl", "Decitabine/Cedazuridine",
        "Ivosidenib", "Enasidenib Mesylate", "Asciminib Hydrochloride",
        "Acalabrutinib", "Acalabrutinib Maleate", "Zanubrutinib", "Tivozanib Hcl",
        "Sotorasib", "Capmatinib Hydrochloride", "Lenvatinib Mesylate",
        "Pacritinib Citrate", "Elacestrant Hcl", "Niraparib/Abiraterone",
        "Bexarotene", "Anagrelide Hcl"
    ],
    "Cardiovascular": [
        "Apixaban", "Rivaroxaban", "Dabigatran Etexilate Mesylate", "Edoxaban Tosylate",
        "Warfarin Sodium", "Clopidogrel Bisulfate", "Ticagrelor", "Prasugrel Hcl",
        "Aspirin/Dipyridamole", "Dipyridamole", "Sacubitril/Valsartan",
        "Lisinopril", "Enalapril Maleate", "Ramipril", "Benazepril Hcl",
        "Captopril", "Fosinopril Sodium", "Quinapril Hcl", "Perindopril Erbumine",
        "Trandolapril", "Moexipril Hcl", "Losartan Potassium", "Valsartan",
        "Irbesartan", "Candesartan Cilexetil", "Olmesartan Medoxomil",
        "Telmisartan", "Azilsartan Medoxomil", "Amlodipine Besylate",
        "Nifedipine", "Felodipine", "Nicardipine Hcl", "Isradipine", "Nisoldipine",
        "Metoprolol Succinate", "Metoprolol Tartrate", "Carvedilol",
        "Bisoprolol Fumarate", "Atenolol", "Propranolol Hcl", "Labetalol Hcl",
        "Nebivolol Hcl", "Nadolol", "Pindolol", "Acebutolol Hcl",
        "Furosemide", "Hydrochlorothiazide", "Chlorthalidone", "Indapamide",
        "Spironolactone", "Eplerenone", "Torsemide", "Bumetanide", "Metolazone",
        "Hydralazine Hcl", "Isosorbide Mononitrate", "Isosorbide Dinitrate",
        "Nitroglycerin", "Digoxin", "Amiodarone Hcl", "Flecainide Acetate",
        "Propafenone Hcl", "Sotalol Hcl", "Dofetilide", "Mexiletine Hcl",
        "Dronedarone Hcl", "Disopyramide Phosphate", "Ranolazine",
        "Ivabradine Hcl", "Diltiazem Hcl", "Verapamil Hcl",
        "Atorvastatin Calcium", "Rosuvastatin Calcium", "Simvastatin",
        "Pravastatin Sodium", "Lovastatin", "Fluvastatin Sodium",
        "Pitavastatin Calcium", "Pitavastatin Magnesium", "Ezetimibe",
        "Alirocumab", "Evolocumab", "Icosapent Ethyl", "Fenofibrate",
        "Gemfibrozil", "Colestipol Hcl", "Colesevelam Hcl", "Cholestyramine (With Sugar)",
        "Bempedoic Acid", "Niacin", "Cilostazol", "Isosorbide Dinit/Hydralazine",
        "Tafamidis", "Tafamidis Meglumine", "Mavacamten", "Vericiguat",
        "Finerenone", "Riociguat", "Macitentan", "Bosentan", "Ambrisentan",
        "Selexipag", "Treprostinil", "Treprostinil Diolamine"
    ],
    "Diabetes": [
        "Metformin Hcl", "Semaglutide", "Tirzepatide", "Dulaglutide",
        "Liraglutide", "Exenatide", "Exenatide Microspheres",
        "Insulin Glargine,hum.Rec.Anlog", "Insulin Glargine-Yfgn",
        "Insulin Degludec", "Insulin Detemir", "Insulin Aspart",
        "Insulin Lispro", "Insulin Regular, Human", "Insulin Nph Human Isophane",
        "Empagliflozin", "Dapagliflozin Propanediol", "Canagliflozin",
        "Ertugliflozin Pidolate", "Sitagliptin Phosphate", "Saxagliptin Hcl",
        "Linagliptin", "Alogliptin Benzoate", "Glipizide", "Glimepiride",
        "Glyburide", "Pioglitazone Hcl", "Nateglinide", "Repaglinide",
        "Acarbose", "Bromocriptine Mesylate", "Pramlintide Acetate",
        "Glucagon", "Dextroamphetamine/Amphetamine"
    ],
    "Psychiatric & Neurological": [
        "Aripiprazole", "Quetiapine Fumarate", "Olanzapine", "Risperidone",
        "Lurasidone Hcl", "Ziprasidone Hcl", "Haloperidol", "Clozapine",
        "Paliperidone", "Iloperidone", "Asenapine Maleate", "Brexpiprazole",
        "Cariprazine Hcl", "Lumateperone Tosylate", "Pimavanserin Tartrate",
        "Sertraline Hcl", "Fluoxetine Hcl", "Escitalopram Oxalate",
        "Citalopram Hydrobromide", "Paroxetine Hcl", "Fluvoxamine Maleate",
        "Venlafaxine Hcl", "Desvenlafaxine", "Duloxetine Hcl",
        "Levomilnacipran Hcl", "Milnacipran Hcl", "Mirtazapine",
        "Bupropion Hcl", "Trazodone Hcl", "Nefazodone Hcl",
        "Amitriptyline Hcl", "Nortriptyline Hcl", "Imipramine Hcl",
        "Desipramine Hcl", "Clomipramine Hcl", "Doxepin Hcl",
        "Lithium Carbonate", "Valproic Acid", "Divalproex Sodium",
        "Lamotrigine", "Carbamazepine", "Oxcarbazepine", "Levetiracetam",
        "Topiramate", "Gabapentin", "Pregabalin", "Phenytoin",
        "Phenobarbital", "Clonazepam", "Diazepam", "Lorazepam",
        "Alprazolam", "Buspirone Hcl", "Hydroxyzine Hcl",
        "Donepezil Hcl", "Memantine Hcl", "Rivastigmine",
        "Galantamine Hbr", "Atomoxetine Hcl", "Methylphenidate Hcl",
        "Dextroamphetamine Sulfate", "Lisdexamfetamine Dimesylate",
        "Modafinil", "Armodafinil", "Zolpidem Tartrate", "Eszopiclone",
        "Zaleplon", "Ramelteon", "Suvorexant", "Lemborexant",
        "Daridorexant Hcl", "Vortioxetine Hydrobromide", "Vilazodone Hcl",
        "Dextromethorphan Hbr/Bupropion", "Dextromethorphan Hbr/Quinidine",
        "Deutetrabenazine", "Tetrabenazine", "Valbenazine Tosylate",
        "Pimozide", "Perphenazine", "Loxapine Succinate", "Thioridazine Hcl",
        "Chlorpromazine Hcl", "Thiothixene", "Trifluoperazine Hcl",
        "Fluphenazine Hcl", "Rasagiline Mesylate", "Selegiline",
        "Pramipexole Di-Hcl", "Ropinirole Hcl", "Rotigotine",
        "Carbidopa/Levodopa", "Entacapone", "Opicapone", "Istradefylline",
        "Droxidopa", "Amantadine Hcl", "Riluzole", "Edaravone",
        "Cannabidiol (Cbd)", "Esketamine Hcl", "Brexanolone"
    ],
    "Infectious Disease & Antiviral": [
        "Nirmatrelvir/Ritonavir", "Molnupiravir", "Oseltamivir Phosphate",
        "Valacyclovir Hcl", "Acyclovir", "Famciclovir", "Ganciclovir",
        "Valganciclovir Hcl", "Letermovir", "Entecavir",
        "Bictegrav/Emtricit/Tenofov Ala", "Dolutegravir Sodium",
        "Elviteg/Cob/Emtri/Tenof Alafen", "Cabotegravir/Rilpivirine",
        "Emtricitabine/Tenofov Alafenam", "Emtricitabine/Tenofovir (Tdf)",
        "Darunavir", "Ritonavir", "Atazanavir Sulfate", "Lopinavir/Ritonavir",
        "Raltegravir Potassium", "Rilpivirine Hcl", "Doravirine",
        "Efavirenz", "Nevirapine", "Etravirine", "Maraviroc",
        "Fostemsavir Tromethamine", "Ibalizumab-Uiyk",
        "Sofosbuvir/Velpatasvir", "Glecaprevir/Pibrentasvir",
        "Ledipasvir/Sofosbuvir", "Isoniazid", "Rifampin", "Rifabutin",
        "Ethambutol Hcl", "Posaconazole", "Itraconazole", "Voriconazole",
        "Fluconazole", "Isavuconazonium Sulfate", "Terbinafine Hcl",
        "Nitazoxanide", "Atovaquone", "Ivermectin", "Albendazole",
        "Azithromycin", "Clarithromycin", "Doxycycline Hyclate",
        "Doxycycline Monohydrate", "Minocycline Hcl", "Amoxicillin",
        "Ciprofloxacin Hcl", "Levofloxacin", "Moxifloxacin Hcl",
        "Linezolid", "Vancomycin Hcl", "Fidaxomicin", "Metronidazole"
    ],
    "Pulmonary & Allergy": [
        "Budesonide/Formoterol Fumarate", "Fluticasone Propion/Salmeterol",
        "Fluticasone/Vilanterol", "Tiotropium Bromide", "Umeclidinium Bromide",
        "Ipratropium Bromide", "Albuterol Sulfate", "Levalbuterol Hcl",
        "Montelukast Sodium", "Zafirlukast", "Theophylline Anhydrous",
        "Roflumilast", "Nintedanib Esylate", "Pirfenidone",
        "Omalizumab", "Mepolizumab", "Benralizumab", "Dupilumab",
        "Tezepelumab-Ekko", "Ciclesonide", "Flunisolide",
        "Beclomethasone Dipropionate", "Mometasone Furoate",
        "Fluticasone Propionate", "Cetirizine Hcl", "Levocetirizine Dihydrochloride",
        "Desloratadine", "Azelastine Hcl", "Cromolyn Sodium",
        "Elexacaftor/Tezacaftor/Ivacaft", "Ivacaftor"
    ],
    "Rheumatology & Immunology": [
        "Adalimumab", "Etanercept", "Infliximab", "Certolizumab Pegol",
        "Golimumab", "Secukinumab", "Ixekizumab", "Ustekinumab",
        "Risankizumab-Rzaa", "Guselkumab", "Sarilumab", "Tocilizumab",
        "Abatacept", "Belimumab", "Tofacitinib Citrate", "Baricitinib",
        "Upadacitinib", "Apremilast", "Deucravacitinib", "Leflunomide",
        "Methotrexate Sodium", "Hydroxychloroquine Sulfate", "Azathioprine",
        "Mycophenolate Mofetil", "Cyclosporine", "Tacrolimus",
        "Colchicine", "Febuxostat", "Allopurinol", "Pegloticase"
    ],
    "Pain & Opioids": [
        "Oxycodone Hcl", "Hydrocodone/Acetaminophen", "Morphine Sulfate",
        "Hydromorphone Hcl", "Fentanyl", "Methadone Hcl", "Buprenorphine Hcl",
        "Buprenorphine Hcl/Naloxone Hcl", "Naltrexone Hcl",
        "Naloxone Hcl", "Tramadol Hcl", "Tapentadol Hcl",
        "Oxymorphone Hcl", "Codeine Sulfate", "Celecoxib",
        "Meloxicam", "Naproxen", "Ibuprofen", "Diclofenac Sodium",
        "Etodolac", "Nabumetone", "Sulindac", "Piroxicam",
        "Indomethacin", "Ketorolac Tromethamine", "Diflunisal",
        "Salsalate", "Pregabalin", "Gabapentin", "Duloxetine Hcl",
        "Cyclobenzaprine Hcl", "Methocarbamol", "Carisoprodol",
        "Metaxalone", "Baclofen", "Tizanidine Hcl", "Orphenadrine Citrate"
    ],
    "Gastrointestinal": [
        "Omeprazole", "Pantoprazole Sodium", "Esomeprazole Magnesium",
        "Lansoprazole", "Rabeprazole Sodium", "Dexlansoprazole",
        "Famotidine", "Cimetidine", "Sucralfate", "Mesalamine",
        "Sulfasalazine", "Balsalazide Disodium", "Infliximab",
        "Vedolizumab", "Ustekinumab", "Linaclotide", "Plecanatide",
        "Lubiprostone", "Prucalopride Succinate", "Tenapanor Hcl",
        "Rifaximin", "Eluxadoline", "Alosetron Hcl", "Lactulose",
        "Methylnaltrexone Bromide", "Naldemedine Tosylate",
        "Naloxegol Oxalate", "Metoclopramide Hcl", "Ondansetron",
        "Aprepitant", "Dicyclomine Hcl", "Hyoscyamine Sulfate",
        "Ursodiol", "Obeticholic Acid", "Cholestyramine (With Sugar)"
    ],
    "Endocrine & Bone": [
        "Levothyroxine Sodium", "Liothyronine Sodium", "Methimazole",
        "Propylthiouracil", "Desmopressin Acetate", "Fludrocortisone Acetate",
        "Prednisone", "Methylprednisolone", "Dexamethasone",
        "Testosterone", "Testosterone Cypionate", "Progesterone, Micronized",
        "Estrogens, Conjugated", "Estradiol", "Raloxifene Hcl",
        "Alendronate Sodium", "Risedronate Sodium", "Ibandronate Sodium",
        "Zoledronic Acid/Mannitol-Water", "Denosumab", "Teriparatide",
        "Abaloparatide", "Romosozumab-Aqqg", "Calcitonin,salmon,synthetic",
        "Calcifediol", "Calcitriol", "Ergocalciferol (Vitamin D2)",
        "Cinacalcet Hcl", "Somatropin", "Lanreotide Acetate",
        "Octreotide Acetate", "Cabergoline", "Bromocriptine Mesylate"
    ],
}

def get_category(drug):
    for cat, drugs in CATEGORIES.items():
        if drug in drugs:
            return cat
    return "Other"

drug_categories = {d: get_category(d) for d in drug_list}
all_categories = ["All"] + sorted(CATEGORIES.keys()) + ["Other"]

# ── Sidebar controls ──────────────────────────────────────────────────────────
st.sidebar.header("Controls")

selected_category = st.sidebar.selectbox("Therapeutic Category", options=all_categories)

if selected_category == "All":
    filtered_drugs = drug_list
else:
    filtered_drugs = [d for d in drug_list if drug_categories[d] == selected_category]

search = st.sidebar.text_input("Search Drug Name", placeholder="Type to filter...")

if search:
    searched_drugs = [d for d in filtered_drugs if search.lower() in d.lower()]
    if not searched_drugs:
        st.sidebar.warning("No matches — showing all drugs.")
        searched_drugs = filtered_drugs
else:
    searched_drugs = filtered_drugs

default_drug = "Lenalidomide" if "Lenalidomide" in searched_drugs else searched_drugs[0]

selected_drug = st.sidebar.selectbox(
    "Select Drug (Generic Name)",
    options=searched_drugs,
    index=searched_drugs.index(default_drug) if default_drug in searched_drugs else 0
)

metric = st.sidebar.radio(
    "Map Metric",
    options=["Claims per 100k Enrollees", "Cost per Enrollee ($)"]
)

# ── Query ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_drug_data(drug_name):
    return pd.read_sql_query("""
        SELECT
            p.Prscrbr_Geo_Desc AS state,
            e.BENE_STATE_ABRVTN AS state_abbr,
            SUM(p.Tot_Clms) AS tot_clms,
            SUM(p.Tot_Benes) AS tot_benes,
            ROUND(SUM(p.Tot_Drug_Cst), 0) AS tot_cost,
            e.PRSCRPTN_DRUG_TOT_BENES AS part_d_enrollees,
            ROUND(SUM(p.Tot_Clms) * 100000.0 / e.PRSCRPTN_DRUG_TOT_BENES, 1) AS clms_per_100k,
            ROUND(SUM(p.Tot_Drug_Cst) / e.PRSCRPTN_DRUG_TOT_BENES, 2) AS cost_per_enrollee
        FROM part_d_geo p
        JOIN state_enrollment e ON p.Prscrbr_Geo_Cd = e.BENE_FIPS_CD
        WHERE p.Prscrbr_Geo_Lvl = 'State'
          AND LOWER(p.Gnrc_Name) = LOWER(?)
        GROUP BY p.Prscrbr_Geo_Desc, e.BENE_STATE_ABRVTN, e.PRSCRPTN_DRUG_TOT_BENES
        ORDER BY clms_per_100k DESC
    """, conn, params=[drug_name])

df = load_drug_data(selected_drug)

if df.empty:
    st.warning(f"No state-level data found for {selected_drug}.")
    st.stop()

# ── Metric setup ──────────────────────────────────────────────────────────────
if metric == "Claims per 100k Enrollees":
    color_col = "clms_per_100k"
    color_label = "Claims per 100k"
else:
    color_col = "cost_per_enrollee"
    color_label = "Cost per Enrollee ($)"

# ── Summary stats ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("National Claims", f"{int(df['tot_clms'].sum()):,}")
col2.metric("National Beneficiaries", f"{int(df['tot_benes'].sum()):,}" if df['tot_benes'].sum() > 0 else "Suppressed")
col3.metric("Total Drug Cost", f"${df['tot_cost'].sum():,.0f}")
col4.metric("States with Data", len(df))

# ── Map ───────────────────────────────────────────────────────────────────────

max_val = df[color_col].max()
color_range = [0, round(max_val * 1.05, 1)]


fig = px.choropleth(
    df,
    locations="state_abbr",
    locationmode="USA-states",
    color=color_col,
    scope="usa",
    color_continuous_scale="Blues",
    range_color=color_range,
    title=f"{selected_drug} — {color_label} by State (2023)",
    hover_name="state",
    hover_data={
        "state_abbr": False,
        "tot_clms": True,
        "tot_benes": True,
        color_col: True
    },
    labels={
        color_col: color_label,
        "tot_clms": "Total Claims",
        "tot_benes": "Total Beneficiaries"
    }
)
fig.update_layout(coloraxis_colorbar=dict(title=color_label), height=550)
st.plotly_chart(fig, use_container_width=True)

# Territories not rendered by Plotly's USA-states scope
excluded = {"Puerto Rico", "Virgin Islands", "Guam", "Unknown"}
top_state = df.loc[df[color_col].idxmax(), "state"]
if top_state in excluded:
    st.info(f"Note: {top_state} has the highest {color_label} for this drug but is not shown on the map. See the state rankings table below.")

# ── Top / Bottom 10 table ─────────────────────────────────────────────────────
st.subheader(f"State Rankings — {color_label}")
col_a, col_b = st.columns(2)

col_rename = {color_col: color_label, "state": "State"}

with col_a:
    st.markdown("**Top 10 States**")
    st.dataframe(
        df[["state", color_col]].head(10).reset_index(drop=True).rename(columns=col_rename),
        use_container_width=True
    )

with col_b:
    st.markdown("**Bottom 10 States**")
    st.dataframe(
        df[["state", color_col]].tail(10).reset_index(drop=True).rename(columns=col_rename),
        use_container_width=True
    )