#!/usr/bin/env python

etype = {
        'A10': 'J',
        'ACRO': 'P',
        'ACR2': 'P',
        'COUG': 'P',
        'JACE': 'P',
        'SACE': 'P',
        'ACRO': 'P',
        'A500': 'P',
        'A700': 'J',
        'G222': 'T',
        'LA60': 'P',
        'AM3': 'P',
        'L90': 'T',
        'M346': 'J',
        'M308': 'P',
        'M326': 'J',
        'M339': 'J',
        'F260': 'P',
        'AB11': 'P',
        'AB15': 'P',
        'AB18': 'P',
        'AB95': 'P',
        'JCOM': 'J',
        'AC50': 'P',
        'AC52': 'P',
        'AC56': 'P',
        'AC68': 'P',
        'AC6L': 'P',
        'AC80': 'T',
        'AC6L': 'P',
        'AC90': 'T',
        'AC95': 'T',
        'AC95': 'T',
        'AC72': 'P',
        'CLB1': 'P',
        'SGUP': 'T',
        'AE45': 'P',
        'L159': 'J',
        'L29': 'J',
        'L39': 'J',
        'L59': 'J',
        'L60': 'P',
        'AR11': 'P',
        'AR15': 'P',
        'CH7A': 'P',
        'N262': 'J',
        'S601': 'J',
        'S210': 'J',
        'AT3P': 'P',
        'AT3T': 'T',
        'AT5T': 'T',
        'AT6T': 'T',
        'AT8T': 'T',
        'BCS1': 'J',
        'BCS3': 'J',
        'A30B': 'J',
        'A306': 'J',
        'A3ST': 'J',
        'A310': 'J',
        'A318': 'J',
        'A319': 'J',
        'A320': 'J',
        'A321': 'J',
        'A19N': 'J',
        'A20N': 'J',
        'A21N': 'J',
        'A330': 'J',
        'A332': 'J',
        'A333': 'J',
        'A340': 'J',
        'A342': 'J',
        'A343': 'J',
        'A345': 'J',
        'A346': 'J',
        'A358': 'J',
        'A359': 'J',
        'A388': 'J',
        'A38F': 'J',
        'A380': 'J',
        'C27J': 'T',
        'AA1': 'P',
        'AA5': 'P',
        'CH7A': 'P',
        'CH7B': 'P',
        'BL8': 'P',
        'AN12': 'T',
        'AN72': 'J',
        'AT43': 'T',
        'AT44': 'T',
        'AT45': 'T',
        'AT72': 'T',
        'AT75': 'T',
        'NOMA': 'T',
        'M110': 'P',
        'HUSK': 'P',
        'PTS1': 'P',
        'PTS2': 'P',
        'EAGL': 'P',
        'SS2T': 'T',
        'DC3T': 'T',
        'AIRD': 'P',
        'AUS6': 'P',
        'PUP': 'P',
        'BASS': 'P',
        'D4': 'P',
        'D5': 'P',
        'BDOG': 'P',
        'B190': 'T',
        'BE55': 'P',
        'BE56': 'P',
        'BE58': 'P',
        'PRM1': 'J',
        'BE40': 'J',
        'BE33': 'P',
        'BE35': 'P',
        'BE36': 'P',
        'B36T': 'P',
        'BE10': 'T',
        'BE30': 'T',
        'B350': 'T',
        'BE9L': 'T',
        'BE9T': 'T',
        'BE20': 'T',
        'BE17': 'P',
        'BE18': 'P',
        'B18T': 'T',
        'BE23': 'P',
        'BE24': 'P',
        'BE24': 'P',
        'BE50': 'P',
        'BE60': 'P',
        'BE65': 'P',
        'BE70': 'P',
        'BE76': 'P',
        'BE77': 'P',
        'BE80': 'P',
        'BE88': 'P',
        'BE95': 'P',
        'BE99': 'T',
        'T34P': 'P',
        'BL8': 'P',
        'BL17': 'P',
        'A50': 'J',
        'B701': 'J',
        'B703': 'J',
        'B702': 'J',
        'B707': 'J',
        'B712': 'J',
        'B717': 'J',
        'B720': 'J',
        'B721': 'J',
        'B722': 'J',
        'B727': 'J',
        'B731': 'J',
        'B732': 'J',
        'B733': 'J',
        'B734': 'J',
        'B735': 'J',
        'B736': 'J',
        'B737': 'J',
        'B738': 'J',
        'B739': 'J',
        'B38M': 'J',
        'B37M': 'J',
        'B39M': 'J',
        'B3XM': 'J',
        'B741': 'J',
        'B742': 'J',
        'B743': 'J',
        'B744': 'J',
        'BLCF': 'J',
        'B747': 'J',
        'B748': 'J',
        'BSCA': 'J',
        'B74S': 'J',
        'B74R': 'J',
        'B752': 'J',
        'B753': 'J',
        'B754': 'J',
        'B757': 'J',
        'B762': 'J',
        'B763': 'J',
        'B764': 'J',
        'B767': 'J',
        'B772': 'J',
        'B773': 'J',
        'B77W': 'J',
        'B77L': 'J',
        'B774': 'J',
        'B777': 'J',
        'B787': 'J',
        'B788': 'J',
        'B789': 'J',
        'B78X': 'J',
        'B17': 'P',
        'B25': 'P',
        'B29': 'P',
        'B52': 'J',
        'F4': 'J',
        'F14': 'J',
        'F15': 'J',
        'F16': 'J',
        'F18': 'J',
        'F22': 'J',
        'F35': 'J',
        'ST75': 'P',
        'HAR': 'J',
        'DC3S': 'P',
        'DC3': 'P',
        'DC4': 'P',
        'DC6': 'P',
        'DC7': 'P',
        'DC8': 'J',
        'DC85': 'J',
        'DC92': 'J',
        'DC93': 'J',
        'DC95': 'J',
        'DC10': 'J',
        'MD82': 'J',
        'MD83': 'J',
        'MD88': 'J',
        'MD90': 'J',
        'MD10': 'J',
        'MD11': 'J',
        'CL30': 'J',
        'CL60': 'J',
        'CRJ1': 'J',
        'CRJ2': 'J',
        'CRJ7': 'J',
        'CRJ9': 'J',
        'CRJX': 'J',
        'GL5T': 'J',
        'GLEX': 'J',
        'LJ24': 'J',
        'LJ25': 'J',
        'LJ31': 'J',
        'LJ35': 'J',
        'LJ40': 'J',
        'LJ45': 'J',
        'LJ55': 'J',
        'LJ60': 'J',
        'LJ75': 'J',
        'DHC5': 'P',
        'DHC6': 'T',
        'DHC7': 'T',
        'DH8A': 'T',
        'DH8B': 'T',
        'DH8C': 'T',
        'DH8D': 'T',
        'ATLA': 'P',
        'RJ1H': 'J',
        'RJ70': 'J',
        'RJ85': 'J',
        'B461': 'J',
        'B462': 'J',
        'B463': 'J',
        'H25A': 'J',
        'JS31': 'T',
        'JS41': 'T',
        'BA11': 'J',
        'TRIS': 'P',
        'BN2T': 'P',
        'BU81': 'P',
        'TNAV': 'P',
        'CL44': 'T',
        'BU31': 'P',
        'BU33': 'P',
        'H111': 'P',
        'C170': 'P',
        'C120': 'P',
        'C140': 'P',
        'C150': 'P',
        'C152': 'P',
        'C162': 'P',
        'CMAS': 'P',
        'C72R': 'P',
        'C172': 'P',
        'C175': 'P',
        'C177': 'P',
        'C77R': 'P',
        'C180': 'P',
        'C182': 'P',
        'C82R': 'P',
        'C185': 'P',
        'C188': 'P',
        'C190': 'P',
        'C195': 'P',
        'C205': 'P',
        'C06T': 'P',
        'C206': 'P',
        'C207': 'P',
        'C07T': 'P',
        'C208': 'T',
        'C210': 'P',
        'P210': 'P',
        'C10T': 'P',
        'C303': 'P',
        'C310': 'P',
        'A37': 'J',
        'T37': 'J',
        'C320': 'P',
        'C335': 'P',
        'P337': 'P',
        'C337': 'P',
        'C340': 'P',
        'COL3': 'P',
        'COL4': 'P',
        'C402': 'P',
        'C02T': 'P',
        'C404': 'P',
        'C411': 'P',
        'C414': 'P',
        'C421': 'P',
        'C425': 'T',
        'C441': 'T',
        'C525': 'J',
        'C25A': 'J',
        'C25B': 'J',
        'C25C': 'J',
        'C500': 'J',
        'C501': 'J',
        'C550': 'J',
        'C551': 'J',
        'C68A': 'J',
        'C25M': 'J',
        'C510': 'J',
        'S550': 'J',
        'C680': 'J',
        'C560': 'J',
        'C650': 'J',
        'C750': 'J',
        'C56X': 'J',
        'C526': 'J',
        'F406': 'T',
        'O1': 'P',
        'SF50': 'J',
        'SR20': 'P',
        'SR22': 'P',
        'SKIM': 'P',
        'AJ27': 'J',
        'C919': 'J',
        'CVLT': 'P',
        'RALL': 'P',
        'TRIN': 'P',
        'TBM7': 'T',
        'TBM8': 'T',
        'TBM9': 'T',
        'F2TH': 'J',
        'FA50': 'J',
        'FA7X': 'J',
        'F900': 'J',
        'MIR2': 'J',
        'FA10': 'J',
        'FA20': 'J',
        'AJ': 'J',
        'DHC2': 'P',
        'DHC3': 'P',
        'DA20': 'P',
        'DA40': 'P',
        'DA42': 'P',
        'DA50': 'P',
        'DA62': 'P',
        'D228': 'T',
        'D328': 'T',
        'EA50': 'J',
        'E110': 'T',
        'E111': 'T',
        'E120': 'T',
        'E121': 'T',
        'E170': 'J',
        'E190': 'J',
        'E195': 'J',
        'IPAN': 'P',
        'TUCA': 'T',
        'E314': 'T',
        'E135': 'J',
        'E35L': 'J',
        'E145': 'J',
        'E45X': 'J',
        'PA25': 'P',
        'E50P': 'J',
        'E55P': 'J',
        'ERCO': 'P',
        'EVSS': 'P',
        'D328': 'J',
        'J328': 'J',
        'SW4': 'T',
        'SW3': 'T',
        'F27': 'T',
        'F28': 'T',
        'RC70': 'P',
        'GLAS': 'P',
        'GLST': 'P',
        'TBM': 'P',
        'AA5': 'P',
        'GA7': 'P',
        'AA5': 'P',
        'AA1': 'P',
        'GLF2': 'J',
        'GLF3': 'J',
        'GALX': 'J',
        'G280': 'J',
        'GLF4': 'J',
        'GLF5': 'J',
        'GA6C': 'J',
        'GLF6': 'J',
        'ASTR': 'J',
        'G150': 'J',
        'AA1': 'P',
        'H25C': 'J',
        'HA4T': 'J',
        'H25B': 'J',
        'HDJT': 'J',
        'JCOM': 'J',
        'JCOM': 'J',
        'WW23': 'J',
        'WW24': 'J',
        'ARVA': 'T',
        'JCOM': 'J',
        'LA25': 'P',
        'LA4': 'P',
        'LA4': 'P',
        'MU2': 'T',
        'ERCO': 'P',
        'M10': 'P',
        'MITE': 'P',
        'M20P': 'P',
        'M20T': 'P',
        'M22': 'P',
        'T6': 'P',
        'NAVI': 'P',
        'AC90': 'P',
        'AC95': 'T',
        'AC11': 'P',
        'SBR1': 'J',
        'SS2P': 'P',
        'BE26': 'P',
        'P180': 'T',
        'PC12': 'T',
        'PC21': 'T',
        'PC6P': 'T',
        'PC6': 'T',
        'J3': 'P',
        'PA18': 'P',
        'PA20': 'P',
        'PA22': 'P',
        'PA23': 'P',
        'PA27': 'P',
        'PA24': 'P',
        'PA24': 'P',
        'P28A': 'P',
        'P28B': 'P',
        'P28R': 'P',
        'P28T': 'P',
        'PA30': 'P',
        'PA31': 'P',
        'PAY1': 'P',
        'PAY2': 'P',
        'PAT4': 'P',
        'PA32': 'P',
        'PA34': 'P',
        'PAY4': 'T',
        'PAY3': 'T',
        'PA44': 'P',
        'PA46': 'P',
        'P46T': 'T',
        'AEST': 'P',
        'AN2': 'P',
        'M18': 'P',
        'TEX2': 'T',
        'Z42': 'P',
        'Z26': 'P',
        'Z43': 'P',
        'Z26': 'T',
        'Z26': 'T',
        'LYSA': 'T',
        'TU16': 'P',
        'T160': 'P',
        'TU95': 'P',
        'TA15': 'P',
        'TB20': 'P',
        'SASP': 'P',
        'FOUG': 'P',
        'VAUT': 'P',
        'S37': 'P',
        'SU2': 'P',
        'SU7': 'J',
        'SU9': 'J',
        'SU11': 'J',
        'SU15': 'J',
        'SU17': 'J',
        'SU24': 'J',
        'SU25': 'J',
        'SU26': 'P',
        'SU29': 'P',
        'SU27': 'J',
        'SU31': 'P',
        'SU32': 'J',
        'SU34': 'J',
        'SU80': 'T',
        'ST75': 'P',
        'G2GL': 'P',
        'MS18': 'P',
        'MS25': 'P',
        'ST10': 'P',
        'TRIN': 'P',
        'TB31': 'P',
        'GA7': 'P',
        'S55P': 'T',
        'S61R': 'T',
        'H53': 'P',
        'F260': 'H',
        'J8A': 'J',
        'G64T': 'P',
        'CONI': 'P',
        'CONC': 'J',
        'L101': 'J',
        'KODI': 'T',
        'P06T': 'T',
        'P8': 'J',
        'PA28': 'P',
        'T154': 'J',
        'IL62': 'J',
        'P28U': 'P',
        'MA60': 'T',
        'M7': 'T',
        'EUFI': 'J',
        'UH1': 'H',
        'C17': 'J',
        'C141': 'J',
        'C5': 'J',
        'SF34': 'T',
        'B58T': 'P',
        'H850': 'J',
        'S76': 'H',
        'Z50': 'P',
        'H60': 'H',
        'CH60': 'H',
        'MH60': 'H',
        'CH47': 'H',
        'A139': 'H',
        'EPIC': 'T',
        'T38': 'J',
        'HERN': 'P',
        'E75S': 'J',
        'B77F': 'J',
        'T144': 'J',
        'MG29': 'J',
        'DR40': 'P',
        'T134': 'J',
        'E175': 'J',
        'AN24': 'T',
        'E75L': 'J',
        'E767': 'J',
        'B60T': 'T',
        'A748': 'T',
        'U2': 'J',
        'PC7': 'T',
        'AS50': 'H',
        'AT46': 'T',
        'RQ1': 'P',
        'MQ9': 'T',
        'L188': 'T',
        'ULAC': 'P',
        'E200': 'P',
        'E230': 'P',
        'E300': 'P',
        'E400': 'P',
        'E500': 'P',
        'A124': 'J',
        'B24': 'P',
        'C130': 'T',
        'PC6T': 'T',
        'T210': 'P',
        'T51': 'P',
        'A148': 'J',
        'AS32': 'H',
        'AS3B': 'H',
        'AS55': 'H',
        'AS65': 'H',
        'EC45': 'H',
        'EC20': 'H',
        'EC30': 'H',
        'EC35': 'H',
        'EC55': 'H',
        'EC25': 'H',
        'TIGR': 'H',
        'BK17': 'H',
        'B412': 'H',
        'C123': 'P',
        'C119': 'P',
        'B06': 'H',
        'B212': 'H',
        'A109': 'H',
        'A119': 'H',
        'A129': 'H',
        'B47G': 'H',
        'B222': 'H',
        'B230': 'H',
        'B407': 'H',
        'B427': 'H',
        'B430': 'H',
        'B06T': 'H',
        'MG21': 'J',
        'D401': 'P',
        'R22': 'H',
        'R44': 'H',
        'DHC8': 'T',
        'R66': 'H',
        'A339': 'J',
        'A350': 'J',
        'ATP': 'T',
        'A400': 'T',
        'EH10': 'H',
        'PA11': 'P',
        'F18H': 'J',
        'VC10': 'J',
        'VULC': 'J',
        'SIRA': 'P',
        'CVLP': 'P',
        'B609': 'H',
        'LEG2': 'P',
        'TOBA': 'P',
        'BT36': 'P',
        'YK40': 'J',
        'WT9': 'P',
        'PZ04': 'P',
        'F18S': 'J',
        'IL96': 'J',
        'SUCO': 'H',
        'F50': 'T',
        'DASH8': 'T',
        'CESSNA SKYHAWK': 'P',
        'ROBINSON R22': 'H',
        'CESSNA 172 SKYHAWK': 'P',
        'CESSNA 172SP': 'P',
        'CESSNA 172': 'P',
        'C172 SKYHAWK': 'P',
        'CESSNA 182': 'P',
        'SAAB 340': 'T',
        'PA28R': 'P',
        'E550': 'J',
        'RV7': 'P',
        'CL35': 'J'
}
