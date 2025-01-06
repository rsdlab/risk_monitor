#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file risk_monitor.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>

import sys,os
import time
import yaml
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist
from unittest import result
import psycopg2 as pg
from datetime import datetime

home_path = os.environ['HOME']

db_file_path = home_path + '/database.yml'

with open(db_file_path, 'r') as file:
    db = yaml.safe_load(file)


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
risk_monitor_spec = ["implementation_id", "risk_monitor", 
         "type_name",         "risk_monitor", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Category", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class risk_monitor
# @brief ModuleDescription
# 
# 
# </rtc-template>

class risk_monitor(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_symptom = OpenRTM_aist.instantiateDataType(RTC.TimedWString)
        """
        """
        self._symptomIn = OpenRTM_aist.InPort("symptom", self._d_symptom)
        self._d_judge = OpenRTM_aist.instantiateDataType(RTC.TimedWString)
        """
        """
        self._judgeOut = OpenRTM_aist.OutPort("judge", self._d_judge)


		


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
        # </rtc-template>


		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
		
        # Set InPort buffers
        self.addInPort("symptom",self._symptomIn)
		
        # Set OutPort buffers
        self.addOutPort("judge",self._judgeOut)
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
        return RTC.RTC_OK
	

    def onActivated(self, ec_id):
 
        return RTC.RTC_OK
	
  
    def onDeactivated(self, ec_id):
        # データベース接続を閉じる
        self.connection.close()
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):
        if self._symptomIn.isNew(): 
            self._d_symptom=self._symptomIn.read()
            input_text = self._d_symptom.data
            print(f"症状  {input_text}")

            # データベースからリスクレベルを取得
            result_db = check_db()

            print(f"リスクレベル: {result_db}")

            # verification関数を呼び出し
            response_text = verification(result_db, input_text)
            print(f"返答: {response_text}")

            self._d_judge.data = response_text

            self._judgeOut.write()
  
        return RTC.RTC_OK
	


# PostgreSQL接続情報
db_config = {
    'host': 'localhost',
    'dbname': db['dbname'],
    'user': db['user'],
    'password': db['password'],
}


def verification(level, input_text):    

    chat = input_text  # サービスから受け取った文字列を使う

    keyword1 = "悪い"
    keyword2 = "良い"
    if keyword1 in chat:
        if level == 6:
            text = "そうですか。今日は病院に行きましょう。"
            speak = 'bad_low'
        elif level == 7:
            text = "そうですか。今日は病院に行きましょう。"
            speak = 'bad_medium'
        elif level == 8:
            text = "そうですか。今日は病院に行きましょう。"
            speak = 'bad_high'
    elif keyword2 in chat:
        if level == 6:
            text = "良かったです。今日も楽しく過ごしましょう。"
            speak = 'good_low'
        elif level == 7:
            text = "良かったです。今日は念の為、病院に行きましょう。"
            speak = 'good_medium'
        elif level == 8:
            text = "良かったです。今日はできるだけ病院に行きましょう。"
            speak = 'good_high'
    else:
        speak = "NO"
    
    return speak

def check_db():
    print("check")


    connection = connect_to_database()
    if not connection:
        return
    try:
        personalid="Person4"



        # 最新のデータを取得
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT ON (typeid) result, typeid, startdate
                FROM result
                WHERE personalid = %s
                AND typeid IN (1, 2, 3, 4)           
                ORDER BY typeid, startdate DESC
            """, (personalid,))
            results = cursor.fetchall()
            

            if results:
                #resultsがNoneでない場合のみ処理を実行
                data_dict = {typeid: {'result': result, 'measurement_date': startdate} for result, typeid, startdate in results}
                print(f"最新のデータ:")
                for typeid, data in data_dict.items():
                    print(f"{typeid} - {data['result']} (計測日時:{data['measurement_date']})")

                # リスク評価
                temperature_score = calculate_temperature_score(data_dict.get(1, {}).get('result', 0))
                blood_pressure_score = calculate_blood_pressure_score(data_dict.get(2, {}).get('result', 0))
                heart_rate_score = calculate_heart_rate_score(data_dict.get(3, {}).get('result', 0))
                oxygen_saturation_score = calculate_oxygen_saturation_score(data_dict.get(4, {}).get('result', 0))
                print(f"\n体温スコア: {temperature_score}")
                print(f"\n血圧スコア: {blood_pressure_score}")
                print(f"\n心拍数スコア: {heart_rate_score}")
                print(f"\nSpO2スコア: {oxygen_saturation_score}")

                total_score = calculate_risk_score(
                    data_dict.get(1, {}).get('result', 0),
                    data_dict.get(2, {}).get('result', 0),
                    data_dict.get(3, {}).get('result', 0),
                    data_dict.get(4, {}).get('result', 0)
                )
                risk_evaluation = evaluate_risk(total_score,temperature_score, blood_pressure_score, heart_rate_score, oxygen_saturation_score)
                print(f"\nトータルスコア: {total_score}")
                print(f"\nリスク評価: {risk_evaluation}") 
                
                if risk_evaluation=="リスク低":
                    risk_number=6
                elif risk_evaluation=="リスク中":
                    risk_number=7
                elif risk_evaluation=="リスク高":
                    risk_number=8
                return risk_number

            else:
                print("指定されたPersonalidのデータが見つかりませんでした。")
                return None
    except Exception as e:
        print(e)
        return None

def connect_to_database():
    try:
        connection = pg.connect(**db_config)
        return connection
    except pg.Error as e:
        print(f"Error: Unable to connect to the database\n{e}")
        return None

def calculate_temperature_score(temperature):
    temperature = float(temperature) #文字列を浮動小数点に変換
    if temperature <= 35.0:
        return 3
    elif 35.1 <= temperature <= 36.0:
        return 1
    elif 36.1 <= temperature <= 38.0:
        return 0
    elif 38.1 <= temperature <= 39.0:
        return 1
    elif temperature >= 39.1:
        return 2

def calculate_blood_pressure_score(blood_pressure):
    # blood_pressure を文字列に変換
    blood_pressure_str = str(blood_pressure)
    # '/' で分割し、最初の要素を取得
    systolic_pressure_str = blood_pressure_str.split('/')[0]
    # systolic_pressure_str を整数に変換
    systolic_pressure = int(systolic_pressure_str)
    
    if systolic_pressure <= 90:
        return 3
    elif 91 <= systolic_pressure <= 100:
        return 2
    elif 101 <= systolic_pressure <= 110:
        return 1
    elif 111 <= systolic_pressure <= 219:
        return 0
    elif systolic_pressure >= 220:
        return 3

def calculate_heart_rate_score(heart_rate):
    # heart_rate を整数に変換
    heart_rate = int(heart_rate)
    if heart_rate <= 40:
        return 3
    elif 41 <= heart_rate <= 50:
        return 1
    elif 51 <= heart_rate <= 90:
        return 0
    elif 91 <= heart_rate <= 110:
        return 1
    elif 111 <= heart_rate <= 130:
        return 2
    elif heart_rate >= 131:
        return 3
    
def calculate_oxygen_saturation_score(oxygen_saturation):
    # soxygen_saturation を整数に変換
    oxygen_saturation = int(oxygen_saturation)
    if oxygen_saturation <= 91:
        return 3
    elif 92 <= oxygen_saturation <= 93:
        return 2
    elif 94 <= oxygen_saturation <= 95:
        return 1
    elif oxygen_saturation >= 96:
        return 0

def calculate_risk_score(temperature, blood_pressure, heart_rate, oxygen_saturation):
    temperature_score = calculate_temperature_score(temperature)
    blood_pressure_score = calculate_blood_pressure_score(blood_pressure)
    heart_rate_score = calculate_heart_rate_score(heart_rate)
    oxygen_saturation_score = calculate_oxygen_saturation_score(oxygen_saturation)

    total_score = temperature_score + blood_pressure_score + heart_rate_score + oxygen_saturation_score
    return total_score

def evaluate_risk(total_score, temperature_score, blood_pressure_score, heart_rate_score, oxygen_saturation_score):
    if 0 <= total_score <= 4 and sum(score == 3 for score in [temperature_score, blood_pressure_score, heart_rate_score, oxygen_saturation_score]) == 0:
        return "リスク低"
    elif total_score >= 7 or (sum(score == 3 for score in [temperature_score, blood_pressure_score, heart_rate_score, oxygen_saturation_score]) >= 2):
        return "リスク高"
    else:
        return "リスク中"
	



def risk_monitorInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=risk_monitor_spec)
    manager.registerFactory(profile,
                            risk_monitor,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    risk_monitorInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("risk_monitor" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()

