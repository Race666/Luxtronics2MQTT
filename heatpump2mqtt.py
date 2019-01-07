#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Reads operation data from Luxtronics driven Heatpumps and publish its Values
# at an MQTT Broker
#
# created: 15.03.2018 Michael Albert info@michlstechblog.info 
#
# References/Thanks to: 
# https://gist.github.com/2ndsky/5443368
# Credits: https://www.domoticz.com/forum/viewtopic.php?f=34&t=8813&sid=9748ddcc7d3ca03e1e3997f548cbeaae&start=20
#          https://knx-user-forum.de/forum/projektforen/edomi/1016455-interesse-an-lbs-f%C3%BCr-luxtronik-2-steuerung
#          https://service.knx-user-forum.de/?comm=download&id=19000682
#
# License:
# Version: v20180315-191000
#
import socket
import struct
import datetime
import paho.mqtt.client as mqtt
import json
# import http.client
##################### Constants ########################
# Heatpump Luxtronik 2.0 IP
sHostHeatpump = '10.200.1.200'
# Heatpump Luxtronik 2.0 port default 8888
iPortHeatpump = 8888
# MQTT Broker
sHostMQTTBroker = '10.200.1.210'
sPortMQTTBroker = 1883
sMQTTClientID = 'heatpump-script'
sUserMQTTBroker = 'openhab'
sPasswordMQTTBroker = 'ASecurePassword'
sPrefixPublishPath='home/heatpump/0/'
########################################## Values #############################
# Source https://service.knx-user-forum.de/?comm=download&id=19000682
aValueDefinition=[{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'UNKNOWN':None},
{'Temperatur_TVL':'Vorlauf Temperatur (°C)'},
{'Temperatur_TRL':'Rücklauf Temperatur(°C)'},
{'Sollwert_TRL_HZ':'Rücklauf Temperatur Soll (°C)'},
{'Temperatur_TRL_ext':'Temperatur RL Sollwert extern (°C)'},
{'Temperatur_THG':'Heissgas Temperatur (°C)'},
{'Temperatur_TA':'Aussentemperatur (°C)'},
{'Mitteltemperatur':'Mitteltemperatur (°C)'},
{'Temperatur_TBW':'Warmwasser Ist (°C)'},
{'Einst_BWS_akt':'Warmwasser Soll (°C)'},
{'Temperatur_TWE':'Wärmequelle-Eintritt (°C)'},
{'Temperatur_TWA':'Wärmequelle-Austritt (°C)'},
{'Temperatur_TFB1':'Mischkreis 1 Vorlauftemperatur (°C)'},
{'Sollwert_TVL_MK':'Mischkreis 1 Vorlauf-Soll-Temperatur (°C)'},
{'Temperatur_RFV':'Raumtemperatur Raumstation 1 (°C)'},
{'Temperatur_TFB2':'Mischkreis 2 Vorlauftemperatur (°C)'},
{'Sollwert_TVL_MK2':'Mischkreis 2 Vorlauf-Soll-Temperatur (°C)'},
{'Temperatur_TSK':'Fühler Solarkollektor (°C)'},
{'Temperatur_TSS':'Fühler Solarspeicher (°C)'},
{'Temperatur_TEE':'Fühler externe Energiequelle (°C)'},
{'ASDin':'Eingang Abtauende, Soledruck, Durchfluss'},
{'BWTin':'Eingang Brauchwarmwasserthermostat'},
{'EVUin':'EVU Sperrzeit (1/0)'},
{'HDin':'Eingang Hochdruck Kältekreis'},
{'MOTin':'Eingang Motorschutz OK'},
{'NDin':'Eingang Niederdruck'},
{'PEXin':'Eingang Überwachungskontakt für Potentiostat'},
{'SWTin':'Eingang Schwimmbadthermostat'},
{'AVout':'Ausgang Abtauventil'},
{'BUPout':'Ausgang Brauchwasserpumpe/Umstellventil'},
{'HUPout':'Ausgang Heizungsumwälzpumpe'},
{'MA1out':'Ausgang Mischkreis 1 Auf'},
{'MZ1out':'Ausgang Mischkreis 1 Zu'},
{'VENout':'Ausgang Ventilation (Lüftung)'},
{'VBOout':'Ausgang Solepumpe/Ventilator'},
{'VD1out':'Ausgang Verdichter 1'},
{'VD2out':'Ausgang Verdichter 2'},
{'ZIPout':'Ausgang Zirkulationspumpe'},
{'ZUPout':'Ausgang Zusatzumwälzpumpe'},
{'ZW1out':'Ausgang Steuersignal Zusatzheizung v. Heizung'},
{'ZW2SSTout':'Ausgang Steuersignal Zusatzheizung/Störsignal'},
{'ZW3SSTout':'Ausgang Zusatzheizung 3'},
{'FP2out':'Ausgang Pumpe Mischkreis 2'},
{'SLPout':'Ausgang Solarladepumpe'},
{'SUPout':'Ausgang Schwimmbadpumpe'},
{'MZ2out':'Ausgang Mischkreis 2 Zu'},
{'MA2out':'Ausgang Mischkreis 2 Auf'},
{'Zaehler_BetrZeitVD1':'Betriebsstunden Verdichter 1 (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitImpVD1':'Impulse Versichter 1'},
{'Zaehler_BetrZeitVD2':'Betriebsstunden Verdichter 2 (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitImpVD2':'Impulse Versichter 2'},
{'Zaehler_BetrZeitZWE1':'Betriebsstunden Zweiter Wärmeerzeuger 1 (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitZWE2':'Betriebsstunden Zweiter Wärmeerzeuger 2 (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitZWE3':'Betriebsstunden Zweiter Wärmeerzeuger 3 (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitWP':'Betriebsstunden Wärmepumpe (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitHz':'Betriebsstunden Heizung (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitBW':'Betriebsstunden Warmwasser (ddd hh:mm:ss)'},
{'Zaehler_BetrZeitKue':'Betriebsstunden Kühlung (ddd hh:mm:ss)'},
{'Time_WPein_akt':'Wärmepumpe läuft seit (hh:mm:ss)'},
{'Time_ZWE1_akt':'Zweiter Wärmeerzeuger 1 läuft seit (hh:mm:ss)'},
{'Time_ZWE2_akt':'Zweiter Wärmeerzeuger 2 läuft seit (hh:mm:ss)'},
{'Timer_EinschVerz':'Netzeinschaltverzögerung (hh:mm:ss)'},
{'Time_SSPAUS_akt':'Schaltspielsperre AUS (hh:mm:ss)'},
{'Time_SSPEIN_akt':'Schaltspielsperre EIN (hh:mm:ss)'},
{'Time_VDStd_akt':'Verdichter Standzeit (hh:mm:ss)'},
{'Time_HRM_akt':'Heizungsregler Mehr-Zeit (hh:mm:ss)'},
{'Time_HRW_akt':'Heizungsregler Weniger-Zeit (hh:mm:ss)'},
{'Time_LGS_akt':'Thermische Desinfektion läuft seit (hh:mm:ss)'},
{'Time_SBW_akt':'Sperre Warmwasser (hh:mm:ss)'},
{'Code_WP_akt':'Wämepumpen Typ'},
{'BIV_Stufe_akt':'Bivalenzstufe'},
{'WP_BZ_akt':'Betriebszustand'},
{'SoftStand1':'Firmwareversion 1 Stelle'},
{'SoftStand2':'Firmwareversion 2 Stelle'},
{'SoftStand3':'Firmwareversion 3 Stelle'},
{'SoftStand4':'Firmwareversion 4 Stelle'},
{'SoftStand5':'Firmwareversion 5 Stelle'},
{'SoftStand6':'Firmwareversion 6 Stelle'},
{'SoftStand7':'Firmwareversion 7 Stelle'},
{'SoftStand8':'Firmwareversion 8 Stelle'},
{'SoftStand9':'Firmwareversion 9 Stelle'},
{'SoftStand10':'Firmwareversion 10 Stelle'},
{'AdresseIP_akt':'IP Adresse'},
{'SubNetMask_akt':'Subnetzmaske'},
{'Add_Broadcast':'Broadcast Adresse'},
{'Add_StdGateway':'Standard Gateway'},
{'ERROR_Time0':'Zeitstempel Fehler 0 im Speicher'},
{'ERROR_Time1':'Zeitstempel Fehler 1 im Speicher'},
{'ERROR_Time2':'Zeitstempel Fehler 2 im Speicher'},
{'ERROR_Time3':'Zeitstempel Fehler 3 im Speicher'},
{'ERROR_Time4':'Zeitstempel Fehler 4 im Speicher'},
{'ERROR_Nr0':'Fehlercode Fehler 0 im Speicher'},
{'ERROR_Nr1':'Fehlercode Fehler 1 im Speicher'},
{'ERROR_Nr2':'Fehlercode Fehler 2 im Speicher'},
{'ERROR_Nr3':'Fehlercode Fehler 3 im Speicher'},
{'ERROR_Nr4':'Fehlercode Fehler 4 im Speicher'},
{'AnzahlFehlerInSpeicher':'Anzahl der Fehler im Speicher'},
{'Switchoff_file_Nr0':'Grund Abschaltung 0 im Speicher'},
{'Switchoff_file_Nr1':'Grund Abschaltung 1 im Speicher'},
{'Switchoff_file_Nr2':'Grund Abschaltung 2 im Speicher'},
{'Switchoff_file_Nr3':'Grund Abschaltung 3 im Speicher'},
{'Switchoff_file_Nr4':'Grund Abschaltung 4 im Speicher'},
{'Switchoff_file_Time0':'Zeitstempel Abschaltung 0 im Speicher'},
{'Switchoff_file_Time1':'Zeitstempel Abschaltung 1 im Speicher'},
{'Switchoff_file_Time2':'Zeitstempel Abschaltung 2 im Speicher'},
{'Switchoff_file_Time3':'Zeitstempel Abschaltung 3 im Speicher'},
{'Switchoff_file_Time4':'Zeitstempel Abschaltung 4 im Speicher'},
{'Comfort_exists':'Comfort Platine installiert'},
{'HauptMenuStatus_Zeile1':'Status Zeile 1'},
{'HauptMenuStatus_Zeile2':'Status Zeile 2'},
{'HauptMenuStatus_Zeile3':'Status Zeile 3'},
{'HauptMenuStatus_Zeit':'Zeit seit / in (in Kombination mit Feld #118)'},
{'HauptMenuAHP_Stufe':'Stufe Ausheizprogramm'},
{'HauptMenuAHP_Temp':'Temperatur Ausheizprogramm (°C)'},
{'HauptMenuAHP_Zeit':'Laufzeit Ausheizprogramm'},
{'SH_BWW':'Brauchwasser aktiv/inaktiv Symbol'},
{'SH_HZ':'Heizmodus'},
{'SH_MK1':'Mischkreis 1 Symbol'},
{'SH_MK2':'Mischkreis 2 Symbol'},
{'Einst_Kurzrpgramm':'Einstellung Kurzprogramm'},
{'StatusSlave_1':'Status Slave 1'},
{'StatusSlave_2':'Status Slave 2'},
{'StatusSlave_3':'Status Slave 3'},
{'StatusSlave_4':'Status Slave 4'},
{'StatusSlave_5':'Status Slave 5'},
{'AktuelleTimeStamp':'Aktuelle Zeit der Wärmepumpe'},
{'SH_MK3':'Mischkreis 3 Symbol'},
{'Sollwert_TVL_MK3':'Mischkreis 3 Vorlauf-Soll-Temperatur (°C)'},
{'Temperatur_TFB3':'Mischkreis 3 Vorlauftemperatur (°C)'},
{'MZ3out':'Ausgang Mischkreis 3 Zu'},
{'MA3out':'Ausgang Mischkreis 3 Auf'},
{'FP3out':'Pumpe Mischkreis 3'},
{'Time_AbtIn':'Abtauen seit (hh:mm:ss)'},
{'Temperatur_RFV2':'Raumtemperatur Raumstation 2 (°C)'},
{'Temperatur_RFV3':'Raumtemperatur Raumstation 3 (°C)'},
{'SH_SW':'Schaltuhr Schwimmbad Symbol'},
{'Zaehler_BetrZeitSW':'Betriebsstundenzähler Schwimmbad (dd hh:mm:ss)'},
{'FreigabKuehl':'Freigabe Kühlung'},
{'AnalogIn':'Analoges Eingangssignal (V)'},
{'SonderZeichen':''},
{'SH_ZIP':'Zirkulationspumpen Symbol'},
{'WebsrvProgrammWerteBeobarten':''},
{'WMZ_Heizung':'Wärmemengenzähler Heizung (kWh)'},
{'WMZ_Brauchwasser':'Wärmemengenzähler Brauchwasser (kWh)'},
{'WMZ_Schwimmbad':'Wärmemengenzähler Schwimmbad (kWh)'},
{'WMZ_Seit':'Wärmemengenzähler Gesamt (kWh)'},
{'WMZ_Durchfluss':'Wärmemengenzähler Durchfluss (l/h)'},
{'AnalogOut1':'Analog Ausgang 1 (V)'},
{'AnalogOut2':'Analog Ausgang 2 (V)'},
{'Time_Heissgas':'Sperre zweiter Verdichter Heissgas'},
{'Temp_Lueftung_Zuluft':'Zulufttemperatur (°C)'},
{'Temp_Lueftung_Abluft':'Ablufttemperatur (°C)'},
{'Zaehler_BetrZeitSolar':'Betriebstundenzähler Solar'},
{'AnalogOut3':'Analog Ausgang 3 (V)'},
{'AnalogOut4':'Analog Ausgang 4 (V)'},
{'Out_VZU':'Zuluft Ventilator (Abtaufunktion)'},
{'Out_VAB':'Abluft Ventilator'},
{'Out_VSK':'Ausgang VSK'},
{'Out_FRH':'Ausgang FRH'},
{'AnalogIn2':'Analog Eingang 2 (V)'},
{'AnalogIn3':'Analog Eingang 3 (V)'},
{'SAXin':'Eingang SAX'},
{'SPLin':'Eingang SPL'},
{'Compact_exists':'Lüftungsplatine verbaut'},
{'Durchfluss_WQ':'Durchfluss Wärmequelle (l/h)'},
{'LIN_exists':'LIN BUS verbaut'},
{'LIN_ANSAUG_VERDAMPFER':'Temperatur Ansaug Verdampfer (°C)'},
{'LIN_ANSAUG_VERDICHTER':'Temperatur Ansaug Verdichter (°C)'},
{'LIN_VDH':'Temperatur Ansaug Verdichter (°C)'},
{'LIN_UH':'Überhitzung (K)'},
{'LIN_UH_Soll':'Überhitzung Soll (K)'},
{'LIN_HD':'Hochdruck (bar)'},
{'LIN_ND':'Niederdruck (bar)'},
{'LIN_VDH_out':'Ausgang Verdichterheizung'},
{'HZIO_PWM':'Steuersignal Umwälzpumpe (%)'},
{'HZIO_VEN':'Ventilator Drehzahl (U/min)'},
{'HZIO_EVU2':''},
{'HZIO_STB':'Sicherheits-Tempeartur-Begrenzer Fussbodenheizung'},
{'SEC_Qh_Soll':'Leistung Sollwert (kWh)'},
{'SEC_Qh_Ist':'Leistung Istwert (kWh)'},
{'SEC_TVL_Soll':'Temperatur Vorlauf Soll (°C)'},
{'SEC_Software':'Software Stand SEC Board'},
{'SEC_BZ':'Betriebszustand SEC Board'},
{'SEC_VWV':'Vierwegeventil'},
{'SEC_VD':'Verdichterdrehzahl (U/min)'},
{'SEC_VerdEVI':'Verdichtertemperatur EVI (Enhanced Vapour Injection) (°C)'},
{'SEC_AnsEVI':'Ansaugtemperatur EVI (°C)'},
{'SEC_UEH_EVI':'Überhitzung EVI (K)'},
{'SEC_UEH_EVI_S':'Überhitzung EVI Sollwert (K)'},
{'SEC_KondTemp':'Kondensationstemperatur (°C)'},
{'SEC_FlussigEx':'Flüssigtemperatur EEV (elektron. Expansionsventil) (°C)'},
{'SEC_UK_EEV':'Unterkühlung EEV (°C)'},
{'SEC_EVI_Druck':'Druck EVI (bar)'},
{'SEC_U_Inv':'Spannung Inverter (V)'},
{'Temperatur_THG_2':'Temperarturfühler Heissgas 2 (°C)'},
{'Temperatur_TWE_2':'Temperaturfühler Wärmequelleneintritt 2 (°C)'},
{'LIN_ANSAUG_VERDAMPFER_2':'Ansaugtemperatur Verdampfer 2 (°C)'},
{'LIN_ANSAUG_VERDICHTER_2':'Ansaugtemperatur Verdichter 2 (°C)'},
{'LIN_VDH_2':'Temperatur Verdichter 2 Heizung (°C)'},
{'LIN_UH_2':'Überhitzung 2 (K)'},
{'LIN_UH_Soll_2':'Überhitzung Soll 2 (K)'},
{'LIN_HD_2':'Hochdruck 2 (bar)'},
{'LIN_ND_2':'Niederdruck 2 (bar)'},
{'HDin_2':'Eingang Druckschalter Hochdruck 2'},
{'AVout_2':'Ausgang Abtauventil 2'},
{'VBOout_2':'Ausgang Solepumpe/Ventilator 2'},
{'VD1out_2':'Ausgang Verdichter 1 / 2'},
{'LIN_VDH_out_2':'Ausgang Verdichter Heizung 2'},
{'Switchoff2_Nr0':'Grund Abschaltung 0 im Speicher'},
{'Switchoff2_Nr1':'Grund Abschaltung 1 im Speicher'},
{'Switchoff2_Nr2':'Grund Abschaltung 2 im Speicher'},
{'Switchoff2_Nr3':'Grund Abschaltung 3 im Speicher'},
{'Switchoff2_Nr4':'Grund Abschaltung 4 im Speicher'},
{'Switchoff2_Time0':'Zeitstempel Abschaltung 0 im Speicher'},
{'Switchoff2_Time1':'Zeitstempel Abschaltung 1 im Speicher'},
{'Switchoff2_Time2':'Zeitstempel Abschaltung 2 im Speicher'},
{'Switchoff2_Time3':'Zeitstempel Abschaltung 3 im Speicher'},
{'Switchoff2_Time4':'Zeitstempel Abschaltung 4 im Speicher'},
{'RBE_RT_Ist':'Raumtemperatur Istwert (°C)'},
{'RBE_RT_Soll':'Raumtemperatur Sollwert (°C)'},
{'Temp_BW_oben':'Temperatur Brauchwasser Oben (°C)'},
{'Code_WP_akt_2':'Wärmepumpen Typ 2'},
{'Freq_VD':'Verdichterfrequenz (Hz)'},
{'LIN_Temp_ND':''},
{'LIN_Temp_HD':''},
{'Abtauwunsch':''},
{'Abtauwunsch_2':''},
{'Freq_Soll':''},
{'Freq_Min':''},
{'Freq_Max':''},
{'VBO_Soll':''},
{'VBO_Ist':''},
{'HZUP_PWM':''},
{'HZUP_Soll':''},
{'HZUP_Ist':''},
{'Temperatur_VLMax':''},
{'Temperatur_VLMax_2':''},
{'SEC_EVi':''},
{'SEC_EEV':''},
{'Time_ZWE3_akt':''}]
###############################################################################
# Gets Value and Description from aValueDefinition by Index
def getValueDefByIndex(iIndex):
	if iIndex >= len(aValueDefinition):
		ValueName='UNKNOWN'
		Description=None
	else:	
		ValueName=list(aValueDefinition[iIndex].keys())[0]
		Description=aValueDefinition[iIndex][list(aValueDefinition[iIndex].keys())[0]]
	return {'ValueName':ValueName,'Description':Description}
###########################################################################
aFieldsInt2Ip=[91,92,93,94]
def int2ip(addr):                                                               
    return socket.inet_ntoa(struct.pack("!I", addr))
###########################################################################	
# String for bool states
def getBoolString(i):
	if i >= 1:
		return "On"
	else:
		return "Off"
###########################################################################
# Field 78, 230
aFieldsHeatPumpType=[78, 230]
def getHeatPumpType(iType):
	hHPTypes={	0:"ERC",
				1:"SW1",
				2:"SW2",
				3:"WW1",
				4:"WW2",
				5:"L1I",
				6:"L2I",
				7:"L1A",
				8:"L2A",
				9:"KSW",
				10:"KLW",
				11:"SWC",
				12:"LWC",
				13:"L2G",
				14:"WZS",
				15:"L1I407",
				16:"L2I407",
				17:"L1A407",
				18:"L2A407",
				19:"L2G407",
				20:"L2G407",
				21:"L1AREV",
				22:"L2AREV",
				23:"WWC1",
				24:"WWC2",
				27:"L1S",
				28:"L1H",
				29:"L2H",
				30:"WZWD",
				31:"ERC",
				40:"WWB_20",
				41:"LD5",
				42:"LD7",
				43:"SW 37_45",
				44:"SW 58_69",
				45:"SW 29_56",
				46:"LD5 (230V)",
				47:"LD7 (230 V)",
				48:"LD9",
				49:"LD5 REV",
				50:"LD7 REV",
				51:"LD5 REV 230V",
				52:"LD7 REV 230V",
				53:"LD9 REV 230V",
				54:"SW 291",
				55:"LW SEC",
				56:"HMD 2",
				57:"MSW 4",
				58:"MSW 6",
				59:"MSW 8",
				60:"MSW 10",
				61:"MSW 12",
				62:"MSW 14",
				63:"MSW 17",
				64:"MSW 19",
				65:"MSW 23",
				66:"MSW 26",
				67:"MSW 30",
				68:"MSW 4S",
				69:"MSW 6S",
				70:"MSW 8S",
				71:"MSW 10S",
				72:"MSW 13S",
				73:"MSW 16S",
				74:"MSW2-6S",
				75:"MSW4-16",
				76:"LDAG",
				77:"LWD90V",
				78:"MSW-12",
				79:"MSW-12S"}
	return hHPTypes.setdefault(iType,"UNKOWN")
###############################################################################	
# Field 117
aFieldsHauptMenuStatus_Zeile1=[117]
def getHauptMenuStatus_Zeile1(i):
	hStatus={0:"Wärmepumpe läuft",
			1:"Wärmepumpe steht",
			2:"Wärmepumpe kommt",
			4:"Fehler",
			5:"Abtauen",
			6:"Warte auf LIN-Verbindung",
			7:"Verdichter heizt auf",
			8:"Pumpenvorlauf"}
	return hStatus.setdefault(i,"UNKOWN")	
###############################################################################	
# Field 118
aFieldsHauptMenuStatus_Zeile2=[118]
def getHauptMenuStatus_Zeile2(i):
	hStatus={0:"seit:",
			1:"in:"}
	return hStatus.setdefault(i,"UNKOWN")		
###############################################################################	
# Field 119
aFieldsHauptMenuStatus_Zeile3=[119]
def getHauptMenuStatus_Zeile3(i):
	hMode={0:"Heizbetrieb",
			1:"keine Anforderung",
			2:"Netz- Einschaltverzoegerung",
			3:"Schaltspielzeit",
			4:"EVU-Sperrzeit",
			5:"Brauchwasser",
			6:"Estrich Programm",
			7:"Abtauen",
			8:"Pumpenvorlauf",
			9:"Thermische Desinfektion",
			10:"Kuehlbetrieb",
			12:"Schwimmbad/Photovoltaik",
			13:"Heizen Ext.",
			14:"Brauchwasser Ext.",
			16:"Durchflussueberwachung",
			17:"Elektrische Zusatzheizung",
			19:"Warmw. Nachheizung"}
	return hMode.setdefault(i,"UNKOWN")	
###############################################################################	
# Field 79
aFieldsBilanzStufe=[79]
def getBilanzStufe(i):
	hStatus={0:"ein Verdichter darf laufen",
			1:"zwei Verdichter dürfen laufen",
			2:"zusätzlicher Wärmeerzeuger darf mitlaufen"}
	return hStatus.setdefault(i,"UNKOWN")
###############################################################################	
# Field 80
aFieldsBetriebsZustand=[80]
def getBetriebsZustand(i):
	hStatus={0:"Heizen",
			1:"Warmwasser",
			2:"Schwimmbad / Photovoltaik",
			3:"EVU",
			4:"Abtauen",
			5:"Keine Anforderung",
			6:"Heizen ext. Energiequelle",
			7:"Kühlbetrieb"}
	return hStatus.setdefault(i,"UNKOWN")	
###############################################################################	
# Fields 106-110, 217-221
aFieldsGrundAbschaltung=[106,107,108,109,110,217,218,219,220,221]
def getGrundAbschaltung(i):
	hStatus={0:"Waermepumpe Stoerung",
			1:"Anlagen Stoerung",
			2:"Betriebsart Zweiter Waermeerzeuger",
			3:"EVU-Sperre",
			5:"Lauftabtau (nur LW-Geraete)",
			6:"Temperatur Einsatzgrenze maximal",
			7:"Temperatur Einsatzgrenze minimal",
			8:"Untere Einsatzgrenze",
			9:"Keine Anforderung"}
	return hStatus.setdefault(i,"UNKOWN")
###############################################################################	
# Fields 125
aFieldsHeizModus=[125]
def getHeizModus(i):	
	hStatus={0:"Abgesenkt",
		1:"Normal",
		2:"Aus"}	
	return hStatus.setdefault(i,"UNKOWN")	
###############################################################################	
# Field 100-104
aFieldsErrorCodeDescription=[100,101,102,103,104]
def getErrorCodeDescription(i):
	hStatus={701:"Niederdruckstörung Bitte Inst. rufen;Niederdruckpressostat im Kältekreis hat mehrmals angesprochen (LW) oder länger als 20 Sekunden (SW). WP auf Leckage, Schaltpunkt Pressostat, Abtauung und TA-min überprüfen.",
			702:"Niederdrucksperre RESET automatisch. nur bei L/W-Geräten möglich: Niederdruck im Kältekreis hat angesprochen. Nach einiger Zeit automatischer WP-Neuanlauf. WP auf Leckage, Schaltpunkt Pressostat, Abtauung und TA-min überprüfen.",
			703:"Frostschutz Bitte Inst. rufen. nur bei L/W-Geräten möglich: Läuft die Wärmepumpe und wird die Temperatur im Vorlauf < 5 °C, wird auf Frostschutz erkannt.  WP-Leistung, Abtauventil und Heizanlage überprüfen.",
			704:"Heissgasstörung Reset in hh:mm. Maximale Temperatur im Heissgas-Kältekreis überschritten. Automatischer WP-Neuanlauf nach hh:mm. Kältemittelmenge, Verdampfung, Überhitzung Vorlauf, Rücklauf und WQ-min überprüfen.",
			705:"Motorschutz VEN Bitte Inst. rufen. nur bei L/W-Geräten möglich: Motorschutz des Ventilators hat angesprochen. Ventilator überprüfen.",
			706:"Motorschutz BSUP Bitte Inst. rufen. nur bei S/W- und W/W-Geräten möglich: Motorschutz der Sole- oder Brunnenwasserumwälzpumpe oder des Verdichters hat angesprochen. Eingestellte Werte, Verdichter, BOSUP überprüfen.",
			707:"Codierung WP Bitte Inst. rufen. Bruch oder Kurzschluss der Kodierungsbrücke in WP nach der Ersteinschaltung. Kodierungswiderstand in WP, Stecker und Verbindungsleitung überprüfen.",
			708:"Fühler Rücklauf Bitte Inst. rufen. Bruch oder Kurzschluss des Rücklauffühlers. Rücklauffühler, Stecker und Verbindungsleitung überprüfen.",
			709:"Fühler Vorlauf Bitte Inst. rufen. Bruch oder Kurzschluss des Vorlauffühlers. Keine Störabschaltung bei S/W- und W/W-Geräten. Vorlauffühler, Stecker und Verbindungsleitung überprüfen.",
			710:"Fühler Heissgas Bitte Inst. rufen. Bruch oder Kurzschluss des Heissgasfühlers im Kältekreis. Heissgasfühler, Stecker und Verbindungsleitung überprüfen.",
			711:"Fühler Aussentemp. Bitte Inst. rufen. Bruch oder Kurzschluss des Aussentemperaturfühlers. Keine Störabschaltung. Festwert auf -5 °C. Aussentemperaturfühler, Stecker und Verbindungsleitung überprüfen.",
			712:"Fühler Warmwasser Bitte Inst. rufen. Bruch oder Kurzschluss des Warmwasserfühlers. Keine Störabschaltung.. Warmwasserfühler, Stecker und Verbindungsleitung überprüfen.",
			713:"Fühler WQ-Ein Bitte Inst. rufen. Bruch oder Kurzschluss des Wärmequellenfühlers (Eintritt). Wärmequellenfühler, Stecker und Verbindungsleitung überprüfen",
			714:"Heissgas WW Reset in hh:mm. Thermische Einsatzgrenze der WP überschritten. Warmwasserbereitung gesperrt für hh:mm. Durchfluss Warmwasser, Wärmetauscher, Warmwasser-Temperatur und Umwälzpumpe Warmwasser überprüfen.",
			715:"Hochdruck-Abschalt. RESET automatisch. Hochdruckpressostat im Kältekreis hat angesprochen. Nach einiger Zeit automatischer WP-Neuanlauf Durchfluss HW, Überströmer, Temperatur und Kondensation überprüfen.",
			716:"Hochdruckstörung Bitte Inst rufen. Hochdruckpressostat im Kältekreis hat mehrfach angesprochen. Durchfluss HW, Überströmer, Temperatur und Kondensation überprüfen.",
			717:"Durchfluss-WQ Bitte Inst rufen. Durchflussschalter bei W/W-Geräten hat während der Vorspülzeit oder des Betriebs angesprochen. Durchfluss, Schaltpunkt DFS, Filter, Luftfreiheit überprüfen",
			718:"Max. Aussentemp. RESET automatisch. nur bei L/W-Geräten möglich: Aussentemperatur hat zulässigen Maximalwert überschritten.. Aussentemperatur und eingestellten Wert überprüfen.",
			719:"Min. Aussentemp. RESET automatisch. nur bei L/W-Geräten möglich: Aussentemperatur hat zulässigen Minimalwert unterschritten.. Aussentemperatur und eingestellten Wert überprüfen.",
			720:"WQ-Temperatur RESET automatisch in hh:mm. nur bei S/W- und W/W-Geräten möglich: Temperatur am Verdampferaustritt ist auf WQ-Seite mehrfach unter den Sicherheitswert gefallen. Automatischer WP-Neuanlauf nach hh:mm. Durchfluss, Filter, Luftfreiheit, Temperatur überprüfen.",
			721:"Niederdruckabschaltung RESET automatisch. Niederdruckpressostat im Kältekreis hat angesprochen. Nach einiger Zeit automatischer WP-Neuanlauf (SW und WW). Schaltpunkt Pressostat, Durchfluss WQ-Seite überprüfen.",
			722:"Tempdiff Heizwasser Bitte Inst rufen. Temperaturspreizung im Heizbetrieb ist negativ (=fehlerhaft). Funktion und Platzierung der Vor- und Rücklauffühler überprüfen.",
			723:"Tempdiff Warmw. Bitte Inst rufen.  Temperaturspreizung im Warmwasserbetrieb ist negativ (=fehlerhaft). Funktion und Platzierung der Vor- und Rücklauffühler überprüfen.",
			724:"Tempdiff Abtauen Bitte Inst rufen. Temperaturspreizung im Heizkreis ist während des Abtauens > 15 K (=Frostgefahr). Funktion und Platzierung der Vor- und Rücklauffühler, Förderleistung HUP, Überströmer und Heizkreise überprüfen.",
			725:"Anlagefehler WW Bitte Inst rufen. Warmwasserbetrieb gestört, gewünschte Speichertemperatur ist weit unterschritten. Umwälzpumpe WW, Speicherfüllung, Absperrschieber und 3-Wege-Ventil überprüfen. Heizwasser und WW entlüften.",
			726:"Fühler Mischkreis 1 Bitte Inst rufen. Bruch oder Kurzschluss des Mischkreisfühlers. Mischkreisfühler, Stecker und Verbindungsleitung überprüfen.",
			727:"Soledruck Bitte Inst rufen. Soledruckpressostat hat während Vorspülzeit oder während des Betriebs angesprochen. Soledruck und Soledruckpressostat überprüfen.",
			728:"Fühler WQ-Aus Bitte Inst. rufen. Bruch oder Kurzschluss des Wärmequellenfühlers am WQ-Austritt Wärmequellenfühler, Stecker und Verbindungsleitung überprüfen.",
			729:"Drehfeldfehler Bitte Inst rufen. Verdichter nach dem Einschalten ohne Leistung. Drehfeld und Verdichter überprüfen.",
			730:"Leistung Ausheizen Bitte Inst rufen. Das Ausheizprogramm konnte eine VL-Temperaturstufe nicht im vorgegebenen Zeitintervall erreichen. Ausheizprogramm läuft weiter..  Leistungsbedarf während des Ausheizens überprüfen.",
			732:"Störung Kühlung Bitte Inst rufen. Die Heizwassertemperatur von 16 °C wurde mehrfach unterschritten. Mischer und Heizungsumwälzpumpe überprüfen.",
			733:"Störung Anode Bitte Inst. rufen. Störmeldeeingang der Fremdstromanode hat angesprochen. Verbindungsleitung Anode und Potenziostat überprüfen. WW-Speicher füllen.",
			734:"Störung Anode Bitte Inst. rufen. Fehler 733 liegt seit mehr als zwei Wochen an und Warmwasserbereitung ist gesperrt. Fehler vorübergehend quittieren, um Warmwasserbereitung wieder freizugeben. Fehler 733 beheben.",
			735:"Fühler Ext. En Bitte Inst rufen. nur bei eingebauter Comfort-/Erweiterungs-Platine möglich: Bruch oder Kurzschluss des Fühlers ?Externe Energiequelle?. Fühler ?Externe Energiequelle?, Steckerund Verbindungsleitung überprüfen.",
			736:"Fühler Solarkollektor Bitte Inst rufen. nur bei eingebauter Comfort-/Erweiterungs-Platine möglich: Bruch oder Kurzschluss des Fühlers ?Solarkollektor?. Fühler ?Solarkollektor?, Stecker undVerbindungsleitung überprüfen.",
			737:"Fühler Solarspeicher Bitte Inst rufen. nur bei eingebauter Comfort-/Erweiterungs-Platine möglich: Bruch oder Kurzschluss des Fühlers ?Solarspeicher?. Fühler ?Solarspeicher?, Stecker und Verbindungsleitung überprüfen.",
			738:"Fühler Mischkreis2 Bitte Inst rufen. nur bei eingebauter Comfort-/Erweiterungs-Platine möglich: Bruch oder Kurzschluss des Fühlers ?Mischkreis2?. Fühler ?Mischkreis2?, Stecker und Verbindungsleitung überprüfen.",
			750:"Fühler Rücklauf extern Bitte Inst. rufen. Bruch oder Kurzschluss des externen Rücklauffühlers. Externer Rücklauffühler, Stecker und Verbindungsleitung überprüfen.",
			751:"Phasenüberwachungsfehler. Phasenfolgerelais hat angesprochen. Überprüfung Drehfeld und Phasenfolgerelais.",
			752:"Phasenüberwachungs / Durchflussfehler. Phasenfolgerelais oder Durchflussschalter hat angesprochen. siehe Fehler Nr. 751 und Nr. 717",
			755:"Verbindung zu Slave verloren Bitte Inst. rufen. Ein Slave hat für mehr als 5 Minuten nicht geantwortet. Netzwerkverbindung, Switch und IP-Adressen prüfen. Gegebenenfalls WP-Suche erneut ausführen.",
			756:"Verbindung zu Master verloren Bitte Inst. rufen. Ein Master hat für mehr als 5 Minuten nicht geantwortet. Netzwerkverbindung, Switch und IP-Adressen prüfen. Gegebenenfalls WP-Suche erneut ausführen.",
			757:"ND-Störung bei WW-Gerät. Niederdruckpressostat bei WW-Gerät hat mehrmals oder länger als 20 Sekunden angesprochen. Bei 3maligem Auftreten dieser Störung kann die Anlage nur vom authorisierten Servicepersonal freigeschaltet werden!",
			758:"Störung Abtauung. Die Abtauung wurde 5mal in Folge über zu niedrige Vorlauftemperatur beendet. Durchfluss prüfen Vorlaufsensor prüfen",
			759:"Meldung TDI. Thermische Desinfektion konnte 3mal in Folge nicht korrekt durchgeführt werden. Einstellung Zweiter Wärmeerzeuger und Sicherheitstemperaturbegrenzer prüfen",
			760:"Störung Abtauung. Abtauung wurde 5mal in Folge über Maximalzeit beendet (starker Wind trifft auf Verdampfer). Ventilator und Verdampfer vor starkem Wind schützen",
			761:"LIN-Verbindung unterbrochen. LIN-Timeout. Kabel/Kontakt prüfen",
			762:"Fühler Ansaug Verdichter. Fühlerfehler Tü (Ansaug Verdichter). Fühler prüfen, evtl. tauschen",
			763:"Fühler Ansaug-Verdampfer. Fühlerfehler Tü1 (Ansaug Verdampfer). Fühler prüfen, evtl. tauschen",
			764:"Fühler Verdichterheizung. Fühlerfehler Verdichterheizung. Fühler prüfen, evtl. tauschen",
			765:"Überhitzung. Überhitzung länger als 5 Minuten unter 2K. Bei Ersteinschaltung. Drehfeld prüfen, sonst Kundendienst rufen",
			766:"Einsatzgrenzen-VD. Betrieb 5 Minuten außerhalb des Einsatzbereichs des Verdichters. Drehfeld prüfen",
			767:"STB E-Stab. STB des Heizstabs am SEC wurde aktiviert. Heizstab überprüfen und Sicherung wieder reindrücken",
			770:"Niedrige Überhitzung. Überhitzung liegt über einen längeren Zeitraum unter dem Grenzwert. Temperaturfühler, Drucksensor und Expansionsventil prüfen",
			771:"Hohe Überhitzung. Überhitzung liegt über einen längeren Zeitraum über dem Grenzwert. Temperaturfühler, Drucksensor, Füllmenge und Expansionsventil prüfen",
			776:"Einsatzgrenzen-VD. Verdichter arbeitet über längeren Zeitraum außerhalb seiner Einsatzgrenzen. Thermodynamik prüfen",
			777:"Expansionsventil. Expansionsventil defekt. Expansionsventil, Verbindungskabel und ggf. SEC-Board prüfen",
			778:"Fühler Niederdruck. Niederdruckfühler defekt. Sensor, Stecker und Verbindungsleitung prüfen",
			779:"Fühler Hochdruck. Hochdruckfühler defekt. Sensor, Stecker und Verbindungsleitung prüfen",
			780:"Fühler EVI. EVI-Fühler defekt. Sensor, Stecker und Verbindungsleitung prüfen",
			781:"Fühler Flüssig, vor Ex-Ventil. Temperaturfühler Flüssig vor Ex-Ventil defekt. Sensor, Stecker und Verbindungsleitung prüfen",
			782:"Fühler EVI Sauggas. Temperaturfühler EVI Sauggas defekt. Sensor, Stecker und Verbindungsleitung prüfen",
			783:"Kommunikation SEC - Inverter. Kommunikation zwischen SEC u. Inverter gestört. Verbindungskabel, Entstörkondensatoren und Verkabelung prüfen",
			784:"VSS gesperrt. Inverter gesperrt. Komplette Anlage 2 Minuten lang spannungslos schalten. Bei wiederholtem Auftreten Inverter und Verdichter prüfen",
			785:"SEC-Board defekt. Fehler im SEC Board festgestellt. SEC Board austauschen",
			786:"Kommunikation SEC - Inverter. Störung der Kommunikation zwischen SEC und HZIO von SEC festgestellt. Kabelverbindung HZ/IO SEC-Board prüfen",
			787:"VD Alarm. Verdichter meldet Fehler. Störung quittieren. Falls Fehler mehrfach auftritt, autorisiertes Servicepersonal (= Kundendienst) rufen",
			788:"Schwerw. Inverter. Fehler. Fehler im Inverter Inverter prüfen",
			789:"LIN/Kodierung nicht vorhanden. Bedienteil konnte keine Kodierung feststellen. Entweder ist die LIN-Verbindung unterbrochen oder der Kodierungswiderstand wird nicht erkannt. Verbindungskabel LIN / Kodierwiderstand prüfen",
			790:"Schwerw. Inverter Fehler. Fehler in der Stromversorgung des Inverters / Verdichters. Verkabelung, Inverter und Verdichter prüfen",
			791:"ModBus Verbindung verloren. SEC-Board seit einiger Zeit nicht mehr erreichbar. 791 wird ausgelöst, wenn zwar eine HZIO-Platine gefunden worden ist (ohne separate Kodierung), allerdings kein SEC-Board daran erkannt werden kann. Sofern es sich um die SECKonfiguration handelt, das ModBus-Kabel zwischen HZIO und SEC Board prüfen. Ebenso das SEC-Board prüfen, ob alles blinkt, wie es soll Falls es KEINE Konfiguration mit SEC-Board ist (z.B., weil es sich um ein P184-Gerät handelt), dann den Kodierungswiderstand der HZIO prüfen",
			792:"LIN-Verbindung unterbrochen. Es konnte keine Grundplatine und auch sonst keine Konfiguration gefunden werden. Kodierungsstecker auf LINPlatine(n) prüfen",
			793:"Schwerw. Inverter. Fehler Temperaturfehler im Inverter. Fehler behebt sich selbst"}
	return hStatus.setdefault(i,"UNKOWN ERROR")	
###############################################################################
# Count Datafields
iDataFields = 0
# Received Data
aData = []

# Socket
oSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
# Connect to Heatpump
oSocket.connect((sHostHeatpump, iPortHeatpump))

# Send to get state
oSocket.send( struct.pack( '!i', 3004))
oSocket.send( struct.pack( '!i', 0))

# Check received packet, 4 Byte as Int must be equal 3004
if struct.unpack( '!i', oSocket.recv(4))[0] != 3004:
    print("Error during request occured.")
    exit(1)
# Receive 4 Bytes as Integer
iStat = struct.unpack( '!i', oSocket.recv(4))[0]
iDataFields = struct.unpack( '!i', oSocket.recv(4))[0]
# Add all Fields to an array
for i in range(iDataFields):
    aData.append(struct.unpack( '!i', oSocket.recv(4))[0])
oSocket.close()
# print("Calculated")
print("                    State : ", iStat)
print("Number of fields received : ",iDataFields)
# print(aData)
print("\n")

# Association Fields to DataType, info: Range range(236,246,1) means Field 236-245
# Float 
rRangeFloatData=[122,136,137,142,143,147,159,160,162,163,168,169,173,183,184,187,188,189,227,228,229,231,232,233]
rRangeFloatData.extend(range(10,29,1))
rRangeFloatData.extend(range(151,158,1))
rRangeFloatData.extend(range(175,182,1))
rRangeFloatData.extend(range(193,212,1))
rRangeFloatData.extend(range(236,246,1))
# Int 
rRangeIntData=[57,59,78,79,80,117,118,119,121,123,135,144,148,149,161,190,191,192,230]
rRangeIntData.extend(range(81,91,1))
rRangeIntData.extend(range(100,111,1))
rRangeIntData.extend(range(125,134,1))
rRangeIntData.extend(range(217,222,1))
# IPAddress Value fields
rRangeIPAddressData=[91,92,93,94]
# Bool
rRangeBoolData=[116,124,138,139,140,146,150,170,171,172,174,182,185,186,234,235]
rRangeBoolData.extend(range(29,56,1))
rRangeBoolData.extend(range(164,168,1))
rRangeBoolData.extend(range(212,217,1))
# Timerelative
rRangeDateDiffData=[56,58,120,141,145,158,248]
rRangeDateDiffData.extend(range(60,78,1))
# Timeabsolute
rRangeDateAbsolute=[134]
rRangeDateAbsolute.extend(range(95,100,1))
rRangeDateAbsolute.extend(range(111,116,1))
rRangeDateAbsolute.extend(range(222,227,1))

# ClientID
oMQTTClient = mqtt.Client(client_id=sMQTTClientID)
# Auth
oMQTTClient.username_pw_set(sUserMQTTBroker, sPasswordMQTTBroker)
# Connect synchronous
oMQTTClient.connect(sHostMQTTBroker, sPortMQTTBroker)
for iIndex in range(10,iDataFields):	
	sPublishPath=sPrefixPublishPath+getValueDefByIndex(iIndex)['ValueName']
	oValue=""
	sDetails=""
	if iIndex in rRangeDateDiffData:
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],"=", (str(datetime.timedelta(seconds=int(aData[iIndex])))))
		oValue=int(aData[iIndex])
		sDetails=str(datetime.timedelta(seconds=int(aData[iIndex])))
	if iIndex in rRangeIntData:	
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],") =", (str(int(aData[iIndex]))))
		oValue=int(aData[iIndex])
		# Any detailed information
		if iIndex in aFieldsHeatPumpType:
			sDetails=getHeatPumpType(oValue)
		if iIndex in aFieldsHauptMenuStatus_Zeile1:
			sDetails=getHauptMenuStatus_Zeile1(oValue)			
		if iIndex in aFieldsHauptMenuStatus_Zeile2:
			sDetails=getHauptMenuStatus_Zeile2(oValue)				
		if iIndex in aFieldsHauptMenuStatus_Zeile3:
			sDetails=getHauptMenuStatus_Zeile3(oValue)
		if iIndex in aFieldsBilanzStufe:
			sDetails=getBilanzStufe(oValue)	
		if iIndex in aFieldsBetriebsZustand:
			sDetails=getBetriebsZustand(oValue)	
		if iIndex in aFieldsGrundAbschaltung:
			sDetails=getGrundAbschaltung(oValue)
		if iIndex in aFieldsHeizModus:
			sDetails=getHeizModus(oValue)			
		if iIndex in aFieldsErrorCodeDescription:
			sDetails=getErrorCodeDescription(oValue)		
	if iIndex in rRangeIPAddressData:	
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],") =", (str(int2ip(int(aData[iIndex]) & 0xffffffff))))
		oValue=int(aData[iIndex]) & 0xffffffff
		sDetails=str(int2ip(int(aData[iIndex]) & 0xffffffff))
	if iIndex in rRangeDateAbsolute:	
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],") =", (str((datetime.datetime.fromtimestamp(int(aData[iIndex]))).strftime("%Y-%m-%d %H:%M:%S"))))
		oValue=int(aData[iIndex])
		sDetails=str((datetime.datetime.fromtimestamp(int(aData[iIndex]))).strftime("%Y-%m-%d %H:%M:%S"))
	if iIndex in rRangeBoolData:
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],") =", getBoolString(int(aData[iIndex])))
		oValue=int(aData[iIndex])
		sDetails=getBoolString(int(aData[iIndex]))
	if iIndex in rRangeFloatData:
		print(getValueDefByIndex(iIndex)['ValueName'],"(",getValueDefByIndex(iIndex)['Description'],") =", (str(float(aData[iIndex]/10))))
		oValue=float(aData[iIndex]/10)
	# Json object
	oPayload=json.dumps({"Field":iIndex,"Name":getValueDefByIndex(iIndex)['ValueName'],"Value":oValue,"Description":getValueDefByIndex(iIndex)['Description'],"Details":sDetails})
	# Publish path
	oMQTTClient.publish(sPublishPath,oPayload)		
# Disconnect
oMQTTClient.disconnect()	
###################### Print some  values to Screen ###########################
# Heatpump Type	
print(getValueDefByIndex(78)['ValueName'],getValueDefByIndex(78)['Description'],"=", getHeatPumpType(int(aData[78])))
# Bilanzstufe
print(getValueDefByIndex(79)['ValueName'],getValueDefByIndex(79)['Description'],"=", getBilanzStufe(int(aData[79])))
# Betriebszustand
print(getValueDefByIndex(80)['ValueName'],getValueDefByIndex(80)['Description'],"=", getBetriebsZustand(int(aData[80])))
# Grundabschaltung
print(getValueDefByIndex(106)['ValueName'],getValueDefByIndex(106)['Description'],"=", getGrundAbschaltung(int(aData[117])))
# HauptMenuStatus_Zeile1
print(getValueDefByIndex(117)['ValueName'],getValueDefByIndex(117)['Description'],"=", getHauptMenuStatus_Zeile1(int(aData[117])))
# HauptMenuStatus_Zeile2
print(getValueDefByIndex(118)['ValueName'],getValueDefByIndex(118)['Description'],"=", getHauptMenuStatus_Zeile2(int(aData[118])))
# HauptMenuStatus_Zeile3
print(aValueDefinition[119][list(aValueDefinition[119].keys())[0]],list(aValueDefinition[119].keys())[0],"=", getHauptMenuStatus_Zeile3(int(aData[119])))
# Letzer Fehler
print(getValueDefByIndex(100)['ValueName'],getValueDefByIndex(100)['Description'],"=", str(int(aData[100])))
print(getValueDefByIndex(100)['ValueName'],getValueDefByIndex(100)['Description'],"=", getErrorCodeDescription(int(aData[100])))
print(getValueDefByIndex(95)['ValueName'],getValueDefByIndex(95)['Description'],"=", str(datetime.datetime.fromtimestamp(int(aData[95]))))
# HeizModus
print(getValueDefByIndex(125)['ValueName'],getValueDefByIndex(125)['Description'],"=", getHeizModus(int(aData[125])))



