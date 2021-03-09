from datetime import date

from cohortextractor import StudyDefinition, patients
import codelists

ref_dat = "2021-03-31"
start_dat = "2020-12-01"


study = StudyDefinition(
    index_date=str(date.today()),  # run_dat
    default_expectations={
        "date": {"earliest": start_dat, "latest": "today"},
        "rate": "uniform",
        "incidence": 0.05,
    },
    population=patients.registered_as_of(
        ref_dat,
        return_expectations={
            "incidence": 0.95,
        },
    ),
    age=patients.age_as_of(
        ref_dat,
        return_expectations={
            "int": {"distribution": "population_ages"},
            "rate": "universal",
        },
    ),
    sex=patients.sex(
        return_expectations={
            "category": {"ratios": {"F": 0.49, "M": 0.49, "U": 0.01, "I": 0.01}},
            "rate": "universal",
        },
    ),
    # Asthma Diagnosis code
    ast_dat=patients.with_these_clinical_events(
        codelists.ast,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Asthma Admission codes
    astadm_dat=patients.with_these_clinical_events(
        codelists.astadm,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Asthma systemic steroid prescription code in month 1
    astrxm1_dat=patients.with_these_medications(
        codelists.astrx,
        returning="date",
        find_last_match_in_period=True,
        on_or_after="index_date - 30 days",
        date_format="YYYY-MM-DD",
    ),
    # Asthma systemic steroid prescription code in month 2
    astrxm2_dat=patients.with_these_medications(
        codelists.astrx,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date - 31 days",
        on_or_after="index_date - 60 days",
        date_format="YYYY-MM-DD",
    ),
    # Asthma systemic steroid prescription code in month 3
    astrxm3_dat=patients.with_these_medications(
        codelists.astrx,
        returning="date",
        find_last_match_in_period=True,
        on_or_before="index_date - 61 days",
        on_or_after="index_date - 90 days",
        date_format="YYYY-MM-DD",
    ),
    # Chronic Respiratory Disease
    resp_cov_dat=patients.with_these_clinical_events(
        codelists.resp_cov,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Chronic heart disease codes
    chd_cov_dat=patients.with_these_clinical_events(
        codelists.chd_cov,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Chronic kidney disease diagnostic codes
    ckd_cov_dat=patients.with_these_clinical_events(
        codelists.ckd_cov,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Chronic kidney disease codes - all stages
    ckd15_dat=patients.with_these_clinical_events(
        codelists.ckd15,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Chronic kidney disease codes-stages 3 - 5
    ckd35_dat=patients.with_these_clinical_events(
        codelists.ckd35,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Chronic Liver disease codes
    cld_dat=patients.with_these_clinical_events(
        codelists.cld,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Diabetes diagnosis codes
    diab_dat=patients.with_these_clinical_events(
        codelists.diab,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Immunosuppression diagnosis codes
    immdx_cov_dat=patients.with_these_clinical_events(
        codelists.immdx_cov,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Immunosuppression medication codes
    immrx_dat=patients.with_these_medications(
        codelists.immrx,
        returning="date",
        find_last_match_in_period=True,
        on_or_after="2020-07-01",
        date_format="YYYY-MM-DD",
    ),
    # Chronic Neurological Disease including Significant Learning Disorder
    cns_cov_dat=patients.with_these_clinical_events(
        codelists.cns_cov,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Asplenia or Dysfunction of the Spleen codes
    spln_cov_dat=patients.with_these_clinical_events(
        codelists.spln_cov,
        returning="date",
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # BMI
    bmi_dat=patients.with_these_clinical_events(
        codelists.bmi,
        returning="date",
        ignore_missing_values=True,
        find_last_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
    bmi_val=patients.with_these_clinical_events(
        codelists.bmi,
        returning="numeric_value",
        ignore_missing_values=True,
        find_last_match_in_period=True,
        on_or_before="index_date",
        return_expectations={
            "float": {"distribution": "normal", "mean": 25, "stddev": 5},
        },
    ),
    # All BMI coded terms
    bmi_stage_dat=patients.with_these_clinical_events(
        codelists.bmi_stage,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Severe Obesity code recorded
    sev_obesity_dat=patients.with_these_clinical_events(
        codelists.sev_obesity,
        returning="date",
        ignore_missing_values=True,
        find_last_match_in_period=True,
        on_or_after="bmi_stage_dat",
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
    ),
    # Diabetes resolved codes
    dmres_dat=patients.with_these_clinical_events(
        codelists.dmres,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Severe Mental Illness codes
    sev_mental_dat=patients.with_these_clinical_events(
        codelists.sev_mental,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Remission codes relating to Severe Mental Illness
    smhres_dat=patients.with_these_clinical_events(
        codelists.smhres,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # High Risk from COVID-19 code
    shield_dat=patients.with_these_clinical_events(
        codelists.shield,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Lower Risk from COVID-19 codes
    nonshield_dat=patients.with_these_clinical_events(
        codelists.nonshield,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # to represent household contact of shielding individual
    hhld_imdef_dat=patients.with_these_clinical_events(
        codelists.hhld_imdef,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Wider Learning Disability
    learndis_dat=patients.with_these_clinical_events(
        codelists.learndis,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # First COVID vaccination administration codes
    covadm1_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "target_disease_matches": "SARS-2 CORONAVIRUS",
        },
        emis={
            "procedure_codes": codelists.covadm1,
        },
        find_first_match_in_period=True,
        on_or_after="2020-11-29",
        date_format="YYYY-MM-DD",
    ),
    # Second COVID vaccination administration codes
    covadm2_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "target_disease_matches": "SARS-2 CORONAVIRUS",
        },
        emis={
            "procedure_codes": codelists.covadm2,
        },
        find_last_match_in_period=True,
        on_or_after="covadm1_dat + 19 days",
        date_format="YYYY-MM-DD",
    ),
    # First Pfizer BioNTech vaccination medication code
    pfd1rx_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": "COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
        },
        emis={
            "product_codes": codelists.pfdrx,
        },
        find_first_match_in_period=True,
        on_or_after="2020-11-29",
        date_format="YYYY-MM-DD",
    ),
    # Second Pfizer BioNTech vaccination medication code
    pfd2rx_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": "COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
        },
        emis={
            "product_codes": codelists.pfdrx,
        },
        find_last_match_in_period=True,
        on_or_after="pfd1rx_dat + 19 days",
        date_format="YYYY-MM-DD",
    ),
    # First Oxford AstraZeneca vaccination medication code
    azd1rx_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
        },
        emis={
            "product_codes": codelists.azdrx,
        },
        find_first_match_in_period=True,
        on_or_after="2020-11-29",
        date_format="YYYY-MM-DD",
    ),
    # Second Oxford AstraZeneca vaccination medication code
    azd2rx_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
        },
        emis={
            "product_codes": codelists.azdrx,
        },
        find_last_match_in_period=True,
        on_or_after="azd1rx_dat + 19 days",
        date_format="YYYY-MM-DD",
    ),
    # First COVID vaccination medication code (any)
    covrx1_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": [
                "COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
                "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
            ],
        },
        emis={
            "product_codes": codelists.covrx,
        },
        find_first_match_in_period=True,
        on_or_after="2020-11-29",
        date_format="YYYY-MM-DD",
    ),
    # Second COVID vaccination medication code (any)
    covrx2_dat=patients.with_vaccination_record(
        returning="date",
        tpp={
            "product_name_matches": [
                "COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
                "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
            ],
        },
        emis={
            "product_codes": codelists.covrx,
        },
        find_last_match_in_period=True,
        on_or_after="covrx1_dat + 19 days",
        date_format="YYYY-MM-DD",
    ),
    # Carer codes
    carer_dat=patients.with_these_clinical_events(
        codelists.carer,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # No longer a carer codes
    notcarer_dat=patients.with_these_clinical_events(
        codelists.notcarer,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Employed by Care Home codes
    carehome_dat=patients.with_these_clinical_events(
        codelists.carehome,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Employed by nursing home codes
    nursehome_dat=patients.with_these_clinical_events(
        codelists.nursehome,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Employed by domiciliary care provider codes
    domcare_dat=patients.with_these_clinical_events(
        codelists.domcare,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Patients in long-stay nursing and residential care
    longres_dat=patients.with_these_clinical_events(
        codelists.longres,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity
    eth2001=patients.with_these_clinical_events(
        codelists.eth2001,
        returning="category",
        find_last_match_in_period=True,
        on_or_before="index_date",
        return_expectations={
            "category": {
                "ratios": {
                    "1": 0.5,
                    "2": 0.25,
                    "3": 0.125,
                    "4": 0.0625,
                    "5": 0.03125,
                    "6": 0.015625,
                    "7": 0.0078125,
                    "8": 0.0078125,
                }
            },
            "rate": "universal",
        },
    ),
    # Any other ethnicity code
    non_eth2001_dat=patients.with_these_clinical_events(
        codelists.non_eth2001,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity not given - patient refused
    eth_notgiptref_dat=patients.with_these_clinical_events(
        codelists.eth_notgiptref,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity not stated
    eth_notstated_dat=patients.with_these_clinical_events(
        codelists.eth_notstated,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Ethnicity no record
    eth_norecord_dat=patients.with_these_clinical_events(
        codelists.eth_norecord,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Pregnancy or Delivery codes recorded in the 8.5 months before audit run date
    pregdel_dat=patients.with_these_clinical_events(
        codelists.pregdel,
        returning="date",
        find_last_match_in_period=True,
        on_or_after="index_date - 253 days",
        date_format="YYYY-MM-DD",
    ),
    # Pregnancy codes recorded in the 8.5 months before the audit run date
    preg_dat=patients.with_these_clinical_events(
        codelists.preg,
        returning="date",
        find_last_match_in_period=True,
        on_or_after="index_date - 253 days",
        date_format="YYYY-MM-DD",
    ),
    # COVID vaccination contraindication codes
    covcontra_dat=patients.with_these_clinical_events(
        codelists.covcontra,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # First COVID vaccination declined
    cov1decl_dat=patients.with_these_clinical_events(
        codelists.cov1decl,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
    # Second COVID vaccination declined
    cov2decl_dat=patients.with_these_clinical_events(
        codelists.cov2decl,
        returning="date",
        find_last_match_in_period=True,
        date_format="YYYY-MM-DD",
    ),
)
