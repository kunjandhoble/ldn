import ConfigParser as cp  # >>>> for python 2
# import configparser as cp #>>>> for python 3
import MySQLdb as mysqldb
import json

from decimal import Decimal

import simplejson


def fetch_data_from_db(sqlquery):
    config = cp.ConfigParser()
    config.read("db_creds")
    name = config.get("ldnlocal", "NAME")
    user = config.get("ldnlocal", "USER")
    pwd = config.get("ldnlocal", "PASSWORD")
    host = config.get("ldnlocal", "HOST")
    db = mysqldb.connect(host=host, user=user, passwd=pwd, db=name)
    cursor = db.cursor()
    cursor.execute(sqlquery)
    data = cursor.fetchall()
    cursor.close()
    return data


def oswestry_data(tablename, patientid):
    print(tablename, patientid)
    osw1, osw2, osw3, osw4, osw5, osw6, osw7, osw8, osw9, osw10, osw_score, fordate = [], [], [], [], [], [], [], [], [], [], [], []
    sqlquery = """
                select * from ldn_local.user_{0} where user_id in
                (
                SELECT user_id FROM ldn_local.monthly_questionnaire where user_id <> 309 and user_id ={1} and
                cdc_id is not null and oswestry_id is not null and weight_id is not null and
                meds_count_id is not null and ldn_type_id is not null order by user_id
                )
                order by user_id, forDate ASC""".format(tablename, patientid)
    data = fetch_data_from_db(sqlquery)
    for row in data:
        osw1.append(row[3])
        osw2.append(row[4])
        osw3.append(row[5])
        osw4.append(row[6])
        osw5.append(row[7])
        osw6.append(row[8])
        osw7.append(row[9])
        osw8.append(row[10])
        osw9.append(row[11])
        osw10.append(row[12])
        osw_score.append(row[13])
        fordate.append(str(row[14]))
    oswestry_table_zipped = list(zip(fordate, osw1, osw2, osw3, osw4, osw5, osw6, osw7, osw8, osw9, osw10, osw_score))
    dc = {'osw1': json.dumps(osw1), 'osw2': json.dumps(osw2), 'osw3': json.dumps(osw3), 'osw4': json.dumps(osw4),
          'osw5': json.dumps(osw5),
          'osw6': json.dumps(osw6), 'osw7': json.dumps(osw7), 'osw8': json.dumps(osw8), 'osw9': json.dumps(osw9),
          'osw10': json.dumps(osw10),
          'osw_score': json.dumps(osw_score), 'oswestry_fordate': json.dumps(fordate),
          'oswestry_table_zipped': oswestry_table_zipped}

    return dc


def cdc_data(tablename, patientid):
    sqlquery = """select * from user_{0} where user_id in
                (
                SELECT user_id
                FROM monthly_questionnaire where user_id <> 309 and user_id ={1} and
                cdc_id is not null and oswestry_id is not null and weight_id is not null and
                meds_count_id is not null and ldn_type_id is not null order by user_id
                )
                order by user_id, dateFor ASC""".format(tablename, patientid)
    data = fetch_data_from_db(sqlquery)
    q1, q2, q3, q4, q5, q6, q7, q8, q9, fordate = [], [], [], [], [], [], [], [], [], []
    for row in data:
        q1.append(row[2])
        q2.append(row[3])
        q3.append(row[4])
        q4.append(row[5])
        q5.append(row[6])
        q6.append(row[7])
        q7.append(row[8])
        q8.append(row[9])
        q9.append(row[10])
        fordate.append(str(row[-1]))
    cdc_table_zipped = list(zip(fordate, q1, q2, q3, q4, q5, q6, q7, q8, q9))
    dc = {'q1': json.dumps(q1), 'q2': json.dumps(q2), 'q3': json.dumps(q3), 'q4': json.dumps(q4), 'q5': json.dumps(q5),
          'q6': json.dumps(q6), 'q7': json.dumps(q7), 'q8': json.dumps(q8), 'q9': json.dumps(q9),
          'cdc_fordate': json.dumps(fordate), 'cdc_table_zipped': cdc_table_zipped}

    return dc


def weight_data(tablename, patientid):
    sqlquery = """select * from user_{0} where user_id in
                  ( SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and user_id ={1} and
                    cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null order by user_id
                  ) order by user_id, forDate ASC""".format(tablename, patientid)
    data = fetch_data_from_db(sqlquery)
    justlb, fordate, prefWt = [], [], "justLb"
    for row in data:
        justlb.append(row[3])
        fordate.append(str(row[-2]))
    weight_table_zipped = list(zip(fordate, justlb, [prefWt] * len(fordate)))
    dc = {'weight_justlb': json.dumps(justlb), 'weight_fordate': json.dumps(fordate), 'weight_prefWt': prefWt,
          'weight_table_zipped': weight_table_zipped}
    return dc


def prescriptionmeds_data(tablename, patientid):
    sqlquery = """select * from user_{0} where user_id in (
                    SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and user_id ={1} and
                    (cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null) order by user_id
                    ) order by user_id, forDate ASC""".format(tablename, patientid)
    data = fetch_data_from_db(sqlquery)
    medscount, fordate = [], []
    for row in data:
        medscount.append(row[2])
        fordate.append(str(row[-1]))
    pres_table_zipped = list(zip(fordate, medscount))
    dc = {'pres_medscount': json.dumps(medscount), 'pres_fordate': json.dumps(fordate),
          'pres_table_zipped': pres_table_zipped}
    return dc


def pain_data(tablename, patientid):
    sqlquery = """SELECT user_id, date_added, pain_value, mood_value, fatigue_value,notes FROM user_{0} where user_id in (
                    SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and user_id ={1} and
                    (cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null) order by user_id
                    ) order by user_id, date_added ASC;""".format(tablename, patientid)
    data = fetch_data_from_db(sqlquery)
    date_added, pain_value, mood_value, fatigue_value = [], [], [], []
    for row in data:
        date_added.append(str(row[1]))
        pain_value.append(row[2])
        mood_value.append(row[3])
        fatigue_value.append(row[4])

    dc = {'pain_date_added': json.dumps(date_added), 'pain_value': json.dumps(pain_value),
          'mood_value': json.dumps(mood_value),
          'fatigue_value': json.dumps(fatigue_value)}
    return dc


def dosehistory_data(tablename, patientid):
    sqlquery = """
        SELECT
          user_research_dose_history.id,
          user_research_dose_history.user_id,
          master_ldn_type.medication_type,
          master_ldn_dose_size.dose_size,
          master_ldn_dosing.ldn_dosing,
          user_research_dose_history.other_dose_size,
          user_research_dose_history.on_prescription,
          user_research_dose_history.dateFor
        FROM
          user_research_dose_history,
          master_ldn_type,
          master_ldn_dose_size,
          master_ldn_dosing
        WHERE
            user_research_dose_history.user_id in (
        SELECT user_id
        FROM monthly_questionnaire where user_id <> 309 and user_id ={1} and
        (cdc_id is not null and oswestry_id is not null and weight_id is not null and
        meds_count_id is not null and ldn_type_id is not null) order by user_id
        ) AND
          master_ldn_type.medication_type_id = user_research_dose_history.dose_type AND
          master_ldn_dosing.ldn_dosing_id = user_research_dose_history.dose_timing AND
          master_ldn_dose_size.ldn_dose_size_id = user_research_dose_history.dose_size
           order by user_id, dateFor ASC;
        """.format(tablename, patientid)
    dosesize, fordate = [], []
    data = fetch_data_from_db(sqlquery)

    # class DecimalJSONEncoder(simplejson.JSONEncoder):
    #     def default(self, o):
    #         if isinstance(o, Decimal):
    #             return str(o)
    #         return super(DecimalJSONEncoder, self).default(o)

    for row in data:
        # dosesize.append(json.dumps(Decimal(row[3]), use_decimal = True))
        fordate.append(str(row[-1]))
        dosesize.append(str(row[3]))
    dc = {'dosehistory_dosesize': simplejson.dumps(dosesize), 'dosehistory_fordate': json.dumps(fordate)}
    return dc


def sleep_data(tablename, patientid):
    sqlquery = """
select date_record, hours_sleep, interruptions, quality, notes from user_{0} where user_id={1}
""".format(tablename, patientid)
    date_record, hours_sleep, interruptions, quality, notes = [], [], [], [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        date_record.append(str(row[0]))
        hours_sleep.append(row[1])
        interruptions.append(row[2])
        quality.append(int(row[3]))
        notes.append(row[4])
    sleep_table_zipped = list(zip(date_record, hours_sleep, interruptions, quality, notes))
    dc = {'sleep_date_record': json.dumps(date_record), 'hours_sleep': json.dumps(hours_sleep),
          'interruptions': json.dumps(interruptions), 'quality': json.dumps(quality),
          'sleep_table_zipped': sleep_table_zipped}

    return dc


# dbname to be used  = === ldnappor_development
def cfsfibrotracker_data(tablename, patientid):
    sqlquery = """SELECT date_added, rating as 'Current Condition'
    FROM user_{0}
    where user_id = {1} order by date_added asc""".format(tablename, patientid)
    date_added, rating = [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        date_added.append(str(row[0]))
        rating.append(row[1])
    cfsfibro_table_zipped = list(zip(date_added, rating))
    dc = {'cfsfibro_date_added': json.dumps(date_added), 'cfsfibro_rating': json.dumps(rating),
          'cfsfibro_table_zipped': cfsfibro_table_zipped}

    return dc


def myday_data(tablename, patientid):
    sqlquery = """SELECT date_added, mvalue FROM user_day_tracker where user_id={1} order by date_added asc""".format(
        tablename, patientid)
    date_added, mvalue = [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        date_added.append(str(row[0]))
        mvalue.append(row[1])
    myday_table_zipped = list(zip(date_added, mvalue))
    dc = {'myday_date_added': json.dumps(date_added), 'mvalue': json.dumps(mvalue),
          'myday_table_zipped': myday_table_zipped}

    return dc


def currentdose_data(tablename, patientid):
    sqlquery = """select cd.user_id, cd.entry_date, mds.dose_size, d.ldn_dosing, t.medication_type
                    from user_ldn_current_dose cd
                    left join master_ldn_dose_size mds ON cd.dose_size=mds.ldn_dose_size_id
                    left join master_ldn_dosing d ON cd.dose_timing = d.ldn_dosing_id
                    left join master_ldn_type t on cd.dose_type = t.medication_type_id
                    where cd.user_id={1}
                    order by cd.entry_date asc""".format(tablename, patientid)
    entry_date, dose_size, ldn_dosing, medication_type = [], [], [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        print(row)
        entry_date.append(str(row[1]))
        dose_size.append(str(row[2]))
        ldn_dosing.append(row[3])
        medication_type.append(row[4])

    dc = {'cdose_entry_date': json.dumps(entry_date), 'cdose_dose_size': json.dumps(dose_size),
          'cdose_ldn_dosing': json.dumps(ldn_dosing),
          'cdose_medication_type': json.dumps(medication_type)}
    return dc


def ldntracker_data(tablename, patientid):
    sqlquery = """
    select concat(tt.date_record,' ',tt.time_record) as date_record,ds.dose_size
from user_ldn_taken_tracker tt
left join user_ldn_current_dose cd on tt.user_ldn_dose_id=cd.id and cd.user_id={1}
left join master_ldn_dose_size ds on cd.dose_size = ds.ldn_dose_size_id and cd.user_id={1}
where tt.user_id={1}""".format(tablename, patientid)

    date_record, dose_size = [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        date_record.append(str(row[0]))
        dose_size.append(str(row[1]))
    ldntracker_table_zippped = list(zip(date_record, dose_size))
    dc = {'ldntracker_date_record': json.dumps(date_record), 'ldntracker_dose_size': json.dumps(dose_size),
          'ldntracker_table_zipped': ldntracker_table_zippped}

    return dc
