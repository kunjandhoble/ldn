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


def oswestry_data(tablename):
    print(tablename)
    osw1, osw2, osw3, osw4, osw5, osw6, osw7, osw8, osw9, osw10, osw_score, fordate = [], [], [], [], [], [], [], [], [], [], [], []
    sqlquery = """select * from ldn_local.user_{} where user_id in
                (
                SELECT user_id FROM ldn_local.monthly_questionnaire where user_id <> 309 and
                cdc_id is not null and oswestry_id is not null and weight_id is not null and
                meds_count_id is not null and ldn_type_id is not null order by user_id
                )
                order by user_id, forDate ASC""".format(tablename)
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

    dc = {'osw1': json.dumps(osw1), 'osw2': json.dumps(osw2), 'osw3': json.dumps(osw3), 'osw4': json.dumps(osw4),
          'osw5': json.dumps(osw5),
          'osw6': json.dumps(osw6), 'osw7': json.dumps(osw7), 'osw8': json.dumps(osw8), 'osw9': json.dumps(osw9),
          'osw10': json.dumps(osw10),
          'osw_score': json.dumps(osw_score), 'fordate': json.dumps(fordate)}

    return dc


def cdc_data(tablename):
    sqlquery = """select * from user_{} where user_id in
                (
                SELECT user_id
                FROM monthly_questionnaire where user_id <> 309 and
                cdc_id is not null and oswestry_id is not null and weight_id is not null and
                meds_count_id is not null and ldn_type_id is not null order by user_id
                )
                order by user_id, dateFor ASC""".format(tablename)
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

    dc = {'q1': json.dumps(q1), 'q2': json.dumps(q2), 'q3': json.dumps(q3), 'q4': json.dumps(q4), 'q5': json.dumps(q5),
          'q6': json.dumps(q6), 'q7': json.dumps(q7), 'q8': json.dumps(q8), 'q9': json.dumps(q9),
          'fordate': json.dumps(fordate)}

    return dc


def weight_data(tablename):
    sqlquery = """select * from user_{} where user_id in
                  ( SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and
                    cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null order by user_id
                  ) order by user_id, forDate ASC""".format(tablename)
    data = fetch_data_from_db(sqlquery)
    justlb, fordate, prefWt = [], [], "justLb"
    for row in data:
        justlb.append(row[3])
        fordate.append(str(row[-2]))

    dc = {'justlb': json.dumps(justlb), 'fordate': json.dumps(fordate), 'prefWt': prefWt}
    return dc


def prescriptionmeds_data(tablename):
    sqlquery = """select * from user_{} where user_id in (
                    SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and
                    (cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null) order by user_id
                    ) order by user_id, forDate ASC""".format(tablename)
    data = fetch_data_from_db(sqlquery)
    medscount, fordate = [], []
    for row in data:
        medscount.append(row[2])
        fordate.append(str(row[-1]))
    dc = {'medscount': json.dumps(medscount), 'fordate': json.dumps(fordate)}
    return dc


def pain_data(tablename):
    sqlquery = """SELECT user_id, date_added, pain_value, mood_value, fatigue_value,notes FROM user_{} where user_id in (
                    SELECT user_id
                    FROM monthly_questionnaire where user_id <> 309 and
                    (cdc_id is not null and oswestry_id is not null and weight_id is not null and
                    meds_count_id is not null and ldn_type_id is not null) order by user_id
                    ) order by user_id, date_added ASC;""".format(tablename)
    data = fetch_data_from_db(sqlquery)
    date_added, pain_value, mood_value, fatigue_value = [], [], [], []
    for row in data:
        date_added.append(str(row[1]))
        pain_value.append(row[2])
        mood_value.append(row[3])
        fatigue_value.append(row[4])

    dc = {'date_added': json.dumps(date_added), 'pain_value': json.dumps(pain_value),
          'mood_value': json.dumps(mood_value),
          'fatigue_value': json.dumps(fatigue_value)}
    return dc


def dosehistory_data(tablename):
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
        FROM monthly_questionnaire where user_id <> 309 and
        (cdc_id is not null and oswestry_id is not null and weight_id is not null and
        meds_count_id is not null and ldn_type_id is not null) order by user_id
        ) AND
          master_ldn_type.medication_type_id = user_research_dose_history.dose_type AND
          master_ldn_dosing.ldn_dosing_id = user_research_dose_history.dose_timing AND
          master_ldn_dose_size.ldn_dose_size_id = user_research_dose_history.dose_size
           order by user_id, dateFor ASC;
        """.format(tablename)
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
    dc = {'dosesize': simplejson.dumps(dosesize), 'fordate': json.dumps(fordate)}
    return dc


def sleep_data(tablename):
    sqlquery = """
    SELECT user_id,date_record, hours_sleep, interruptions, quality
    FROM ldn_local.user_{}
    where user_id in (
    SELECT user_id
    FROM ldn_local.monthly_questionnaire where user_id <> 309 and
    (cdc_id is not null and oswestry_id is not null and weight_id is not null and
    meds_count_id is not null and ldn_type_id is not null) order by user_id
    ) order by user_id, date_record ASC""".format(tablename)
    date_record, hours_sleep, interruptions, quality = [], [], [], []
    data = fetch_data_from_db(sqlquery)
    for row in data:
        date_record.append(str(row[1]))
        hours_sleep.append(row[2])
        interruptions.append(row[3])
        quality.append(int(row[4]))
    dc = {'date_record': json.dumps(date_record), 'hours_sleep': json.dumps(hours_sleep),
          'interruptions': json.dumps(interruptions), 'quality': json.dumps(quality)}

    return dc
