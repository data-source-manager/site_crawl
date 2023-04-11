from apps.appbase import AppConfig
from site_crawl.spiders import parser

Apps = {

    # 1: AppConfig(
    #     appid=1,
    #     appname='1_TassParser',
    #     appclass=parser.TassParser,
    #     appdomain='tass.ru'
    # ),
    # # post请求
    # 2: AppConfig(
    #     appid=2,
    #     appname='2_TassComParser',
    #     appclass=parser.TassComParser,
    #     appdomain='tass.com'
    # ),
    # 3: AppConfig(
    #     appid=3,
    #     appname='3_uniindia',
    #     appclass=parser.UniIndiaParser,
    #     appdomain='www.uniindia.com'
    # ),
    #
    1001: AppConfig(
        appid=1001,
        appname='1001_gov',
        appclass=parser.USA_gaoParser,
        appdomain='www.gao.gov'
    ),
    1002: AppConfig(
        appid=1002,
        appname='1002_pmgov',
        appclass=parser.AU_pmgovParser,
        appdomain='www.pm.gov.au'
    ),
    1003: AppConfig(
        appid=1003,
        appname='1003_europa',
        appclass=parser.FR_europaParser,
        appdomain='frontex.europa.eu'
    ),

    1004: AppConfig(
        appid=1004,
        appname='1004_consilium',
        appclass=parser.Euconsilium_europaParser,
        appdomain='consilium.europa.eu'
    ),
    6: AppConfig(
        appid=6,
        appname='6_cecc',
        appclass=parser.CeccParser,
        appdomain='www.cecc.gov'
    ),
    3000: AppConfig(
        appid=3000,
        appname='3000_difesa',
        appclass=parser.DifesaParser,
        appdomain='difesa.it'
    ),
    3001: AppConfig(
        appid=3001,
        appname='3001_bmvg',
        appclass=parser.BmvgParser,
        appdomain='bmvg.de'
    ),
    7: AppConfig(
        appid=7,
        appname='7_usawc',
        appclass=parser.UsawcParser,
        appdomain='usawc.org'
    ),
    8: AppConfig(
        appid=8,
        appname='8_ndu_edu',
        appclass=parser.NduParser,
        appdomain='ndu_edu'
    ),
    9: AppConfig(
        appid=9,
        appname='9_cgsr',
        appclass=parser.CgsrParser,
        appdomain='cgsr.llnl.gov'
    ),
    10: AppConfig(
        appid=10,
        appname='10_minister',
        appclass=parser.MinisterParser,
        appdomain='www.minister.defence.gov.au'
    ),
    11: AppConfig(
        appid=11,
        appname='11_korea',
        appclass=parser.KoreaParser,
        appdomain='www.korea.net'
    ),
    12: AppConfig(
        appid=12,
        appname='12_wciom',
        appclass=parser.WciomParser,
        appdomain='www.wciom.ru'
    ),
    13: AppConfig(
        appid=13,
        appname='13_svop',
        appclass=parser.SvopParser,
        appdomain='svop.ru'
    ),
    15: AppConfig(
        appid=15,
        appname='15_svop',
        appclass=parser.TsjsParser,
        appdomain='www.tsjs.org.tw'
    ),
    16: AppConfig(
        appid=16,
        appname='16_texas',
        appclass=parser.TexasParser,
        appdomain='tmd.texas.gov'
    ),
    17: AppConfig(
        appid=17,
        appname='17_texas',
        appclass=parser.UsaceParser,
        appdomain='www.hnc.usace.army.mil'
    ),
    18: AppConfig(
        appid=18,
        appname='18_history',
        appclass=parser.HistoryParser,
        appdomain='www.history.navy.mil'
    ),
    19: AppConfig(
        appid=19,
        appname='19_med',
        appclass=parser.MedParser,
        appdomain='www.med.navy.mil'
    ),
    20: AppConfig(
        appid=20,
        appname='20_blueangels',
        appclass=parser.BlueangelsParser,
        appdomain='www.blueangels.navy.mil'
    ),
    21: AppConfig(
        appid=21,
        appname='21_blueangels',
        appclass=parser.JbleParser,
        appdomain='www.jble.af.mil'
    ),
    22: AppConfig(
        appid=22,
        appname='22_cnmoc',
        appclass=parser.CnmocParser,
        appdomain='www.cnmoc.usff.navy.mil'
    ),
    23: AppConfig(
        appid=23,
        appname='23_navfac',
        appclass=parser.NavfacParser,
        appdomain='www.navfac.navy.mil'
    ),
    24: AppConfig(
        appid=24,
        appname='24_navifor',
        appclass=parser.NaviforParser,
        appdomain='www.navifor.usff.navy.mil'
    ),
    25: AppConfig(
        appid=25,
        appname='25_navifor',
        appclass=parser.MckinseyParser,
        appdomain='www.navifor.usff.navy.mil'
    ),
    26: AppConfig(
        appid=26,
        appname='26_usfj',
        appclass=parser.UsfjParser,
        appdomain='www.usfj.mil'
    ),
    27: AppConfig(
        appid=27,
        appname='27_usfk',
        appclass=parser.UsfkParser,
        appdomain='www.usfk.mil'
    ),
    28: AppConfig(
        appid=28,
        appname='28_usar_army',
        appclass=parser.UsarParser,
        appdomain='www.usar.army.mil'
    ),
    # ssl error
    # 29: AppConfig(
    #     appid=29,
    #     appname='29_usariem',
    #     appclass=parser.UsariemParser,
    #     appdomain='usariem.health.mil'
    # ),
    30: AppConfig(
        appid=30,
        appname='30_jacksonville',
        appclass=parser.JacksonvilleParser,
        appdomain='jacksonville.tricare.mil'
    ),
    31: AppConfig(
        appid=31,
        appname='31_rader',
        appclass=parser.RaderParser,
        appdomain='rader.tricare.mil'
    ),
    # ssl error
    # 32: AppConfig(
    #     appid=32,
    #     appname='32_mrdc',
    #     appclass=parser.MrdcParser,
    #     appdomain='mrdc.health.mil'
    # ),
    # 403
    33: AppConfig(
        appid=33,
        appname='33_kcfr',
        appclass=parser.KcfrParser,
        appdomain='www.kcfr.or.kr'
    ),
    34: AppConfig(
        appid=34,
        appname='34_yahoo',
        appclass=parser.JpYahooParser,
        appdomain='news.yahoo.co.jp'
    ),
    35: AppConfig(
        appid=35,
        appname='35_kyoto',
        appclass=parser.JpkyotoParser,
        appdomain='www.kyoto-np.co.jp'
    ),
    36: AppConfig(
        appid=36,
        appname='36_prnewswire',
        appclass=parser.UsaPrnewswireParser,
        appdomain='www.prnewswire.com'
    ),
    37: AppConfig(
        appid=37,
        appname='37_nouvelobs',
        appclass=parser.FrNouvelobsParser,
        appdomain='www.nouvelobs.com'
    ),
    38: AppConfig(
        appid=38,
        appname='38_nouvelobs',
        appclass=parser.FrlesechosParser,
        appdomain='www.lesechos.fr'
    ),
    39: AppConfig(
        appid=39,
        appname='39_nouvelobs',
        appclass=parser.RuThemoscowtimesParser,
        appdomain='www.themoscowtimes.com'
    ),
    40: AppConfig(
        appid=40,
        appname='40_leparisien',
        appclass=parser.FrleparisienParser,
        appdomain='www.leparisien.fr'
    ),
    41: AppConfig(
        appid=41,
        appname='41_lemonde',
        appclass=parser.FrLemondeParser,
        appdomain='www.lemonde.fr'
    ),
    42: AppConfig(
        appid=42,
        appname='42_munhwa',
        appclass=parser.KrMunhwaParser,
        appdomain='www.munhwa.com'
    ),
    43: AppConfig(
        appid=43,
        appname='43_navifor',
        appclass=parser.KrasiaeParser,
        appdomain='www.asiae.co.kr'
    ),
    45: AppConfig(
        appid=45,
        appname='45_kommersant',
        appclass=parser.RukommersantParser,
        appdomain='www.kommersant.ru'
    ),
    46: AppConfig(
        appid=46,
        appname='46_straitstimes',
        appclass=parser.SgstraitstimesParser,
        appdomain='tnp.straitstimes.com'
    ),
    47: AppConfig(
        appid=47,
        appname='47_hankyung',
        appclass=parser.KrhankyungParser,
        appdomain='www.hankyung.com'
    ),
    48: AppConfig(
        appid=48,
        appname='48_kln',
        appclass=parser.MyklnParser,
        appdomain='www.kln.gov.my'
    ),
    49: AppConfig(
        appid=49,
        appname='49_nation',
        appclass=parser.KenolParser,
        appdomain='nation.africa'
    ),
    50: AppConfig(
        appid=50,
        appname='50_larazon',
        appclass=parser.EslarazonParser,
        appdomain='www.larazon.es'
    ),
    51: AppConfig(
        appid=51,
        appname='51_larazon',
        appclass=parser.FrmidilibreParser,
        appdomain='www.midilibre.fr'
    ),
    52: AppConfig(
        appid=52,
        appname='52_newsweek',
        appclass=parser.PlNewsweekParser,
        appdomain='www.newsweek.pl'
    ),
    53: AppConfig(
        appid=53,
        appname='53_rp',
        appclass=parser.PlRparser,
        appdomain='www.rp.pl'
    ),
    56: AppConfig(
        appid=56,
        appname='56_urm',
        appclass=parser.LtUrmParser,
        appdomain='urm.lt'
    ),
    57: AppConfig(
        appid=57,
        appname='57_rsis',
        appclass=parser.SgRsisParser,
        appdomain='www.rsis.edu.sg'
    ),
    60: AppConfig(
        appid=60,
        appname='60_gov',
        appclass=parser.UsaCentcomParser,
        appdomain='www.centcom.mil'
    ),
    61: AppConfig(
        appid=61,
        appname='61_southcom',
        appclass=parser.UsaSouthcomParser,
        appdomain='www.southcom.mil'
    ),
    62: AppConfig(
        appid=62,
        appname='62_eucom',
        appclass=parser.UsaEucomParser,
        appdomain='www.eucom.mil'
    ),
    67: AppConfig(
        appid=67,
        appname='67_cybercom',
        appclass=parser.UsaCybercomParser,
        appdomain='www.cybercom.mil'
    ),
    68: AppConfig(
        appid=68,
        appname='68_ustranscom',
        appclass=parser.UsaUstranscomParser,
        appdomain='www.ustranscom.mil'
    ),
    69: AppConfig(
        appid=69,
        appname='69_msc',
        appclass=parser.UsaMscParser,
        appdomain='www.msc.usff.navy.mil'
    ),
    70: AppConfig(
        appid=70,
        appname='70_governo',
        appclass=parser.ItgovernoParser,
        appdomain='www.governo.it'
    ),
    # 71: AppConfig(
    #     appid=71,
    #     appname='71_esercito',
    #     appclass=parser.ItEsercitoParser,
    #     appdomain='www.esercito.difesa.it'
    # ),
    72: AppConfig(
        appid=72,
        appname='72_marina',
        appclass=parser.ItMarinaParser,
        appdomain='www.marina.difesa.it'
    ),
    73: AppConfig(
        appid=73,
        appname='73_stjornarradid',
        appclass=parser.IsStjornarradidParser,
        appdomain='www.stjornarradid.is'
    ),
    74: AppConfig(
        appid=74,
        appname='74_c3f',
        appclass=parser.UsaC3fParser,
        appdomain='www.c3f.navy.mil'
    ),
    75: AppConfig(
        appid=75,
        appname='75_c3f',
        appclass=parser.TwCnaParser,
        appdomain='www.cna.com.tw'
    ),
    76: AppConfig(
        appid=76,
        appname='76_voachinese',
        appclass=parser.UsaVoachineseParser,
        appdomain='www.voachinese.com'
    ),
    77: AppConfig(
        appid=77,
        appname='77_washingtonpost',
        appclass=parser.UsaWashingtonpostParser,
        appdomain='www.washingtonpost.com'
    ),
    78: AppConfig(
        appid=78,
        appname='78_reuters',
        appclass=parser.UkReutersParser,
        appdomain='www.reuters.com'
    ),
    79: AppConfig(
        appid=79,
        appname='79_interfax',
        appclass=parser.RuinterfaxParser,
        appdomain='interfax.com'
    ),
    80: AppConfig(
        appid=80,
        appname='80_ansa',
        appclass=parser.ItansaParser,
        appdomain='www.ansa.it'
    ),
    81: AppConfig(
        appid=81,
        appname='81_upi',
        appclass=parser.UsaUpiParser,
        appdomain='www.upi.com'
    ),
    82: AppConfig(
        appid=82,
        appname='82_ait',
        appclass=parser.UsaAitParser,
        appdomain='www.ait.org.tw'
    ),
    83: AppConfig(
        appid=83,
        appname='83_ytn',
        appclass=parser.KrYtnParser,
        appdomain='www.ytn.co.kr'
    ),
    84: AppConfig(
        appid=84,
        appname='84_france24',
        appclass=parser.FrFrance24Parser,
        appdomain='www.france24.com'
    ),
    85: AppConfig(
        appid=85,
        appname='85_france24',
        appclass=parser.QaAljazeeraParser,
        appdomain='chinese.aljazeera.net'
    ),
    86: AppConfig(
        appid=86,
        appname='86_npr',
        appclass=parser.UsaNprParser,
        appdomain='www.npr.org'
    ),
    87: AppConfig(
        appid=87,
        appname='87_rfi',
        appclass=parser.FrRfiParser,
        appdomain='www.rfi.fr'
    ),
    88: AppConfig(
        appid=88,
        appname='88_rfi_cn',
        appclass=parser.FrRfiCnParser,
        appdomain='www.rfi.fr/cn'
    ),
    89: AppConfig(
        appid=89,
        appname='89_dw',
        appclass=parser.DeDwParser,
        appdomain='www.dw.com'
    ),
    90: AppConfig(
        appid=90,
        appname='90_apnews',
        appclass=parser.UsaApnewsParser,
        appdomain='apnews.com'
    ),
    91: AppConfig(
        appid=91,
        appname='91_koreaherald',
        appclass=parser.UkKoreaheraldParser,
        appdomain='www.koreaherald.com'
    ),
    # 付费
    # 92: AppConfig(
    #     appid=92,
    #     appname='92_tass',
    #     appclass=parser.RuTassParser,
    #     appdomain='tass.ru'
    # ),
    93: AppConfig(
        appid=93,
        appname='93_csis',
        appclass=parser.UsaCsisParser,
        appdomain='www.csis.org'
    ),
    94: AppConfig(
        appid=94,
        appname='94_foxnews',
        appclass=parser.UsaFoxnewsParser,
        appdomain='www.foxnews.com'
    ),
    95: AppConfig(
        appid=95,
        appname='95_heritage',
        appclass=parser.UsaHeritageParser,
        appdomain='www.heritage.org'
    ),
    96: AppConfig(
        appid=96,
        appname='96_heritage',
        appclass=parser.UsaCfrParser,
        appdomain='www.cfr.org'
    ),
    97: AppConfig(
        appid=97,
        appname='97_usip',
        appclass=parser.UsaUsipParser,
        appdomain='www.usip.org'
    ),
    98: AppConfig(
        appid=98,
        appname='98_newsweek',
        appclass=parser.UsaNewsweekParser,
        appdomain='www.newsweek.com'
    ),
    99: AppConfig(
        appid=99,
        appname='99_newsweek',
        appclass=parser.UsaNavalParser,
        appdomain='www.naval-technology.com'
    ),
    100: AppConfig(
        appid=100,
        appname='100_marines',
        appclass=parser.UsaMarinesParser,
        appdomain='www.marines.mil'
    ),
    101: AppConfig(
        appid=101,
        appname='101_eapowermagazine',
        appclass=parser.UsaSeapowermagazineParser,
        appdomain='eapowermagazine.org'
    ),
    102: AppConfig(
        appid=102,
        appname='102_thedefensepost',
        appclass=parser.UsaThedefensepostParser,
        appdomain='www.thedefensepost.com'
    ),
    103: AppConfig(
        appid=103,
        appname='103_cpf',
        appclass=parser.UsaCpfParser,
        appdomain='www.cpf.navy.mil'
    ),
    104: AppConfig(
        appid=104,
        appname='104_asia',
        appclass=parser.JpasiaParser,
        appdomain='asia.nikkei.co'
    ),
    105: AppConfig(
        appid=105,
        appname='105_cnas',
        appclass=parser.UsaCnasParser,
        appdomain='www.cnas.org'
    ),
    106: AppConfig(
        appid=106,
        appname='106_pf',
        appclass=parser.TwPfParser,
        appdomain='www.pf.org.tw'
    ),
    107: AppConfig(
        appid=107,
        appname='107_worldjournal',
        appclass=parser.UsaWorldjournalParser,
        appdomain='www.worldjournal.com'
    ),
    108: AppConfig(
        appid=108,
        appname='108_asiatimes',
        appclass=parser.HkAsiatimesParser,
        appdomain='asiatimes.com'
    ),
    109: AppConfig(
        appid=109,
        appname='109_asiatimes',
        appclass=parser.UsaDefensenewsParser,
        appdomain='www.defensenews.com'
    ),
    110: AppConfig(
        appid=110,
        appname='110_focustaiwan',
        appclass=parser.UsaFocustaiwanParser,
        appdomain='focustaiwan.tw'
    ),
    111: AppConfig(
        appid=111,
        appname='111_militarytimes',
        appclass=parser.UsaMilitarytimesParser,
        appdomain='www.militarytimes.comw'
    ),
    112: AppConfig(
        appid=112,
        appname='112_eurasiantimes',
        appclass=parser.ChEurasiantimesParser,
        appdomain='eurasiantimes.com'
    ),
    113: AppConfig(
        appid=113,
        appname='113_newsis',
        appclass=parser.KrNewsisParser,
        appdomain='www.newsis.com'
    ),
    114: AppConfig(
        appid=114,
        appname='114_cbsnews',
        appclass=parser.UsaCbsnewsParser,
        appdomain='www.cbsnews.com'
    ),
    115: AppConfig(
        appid=115,
        appname='115_nbcnews',
        appclass=parser.UsaNbcnewsParser,
        appdomain='www.nbcnews.com'
    ),
    116: AppConfig(
        appid=116,
        appname='116_huffpost',
        appclass=parser.UsaHuffpostParser,
        appdomain='www.huffpost.com'
    ),
    117: AppConfig(
        appid=117,
        appname='117_donga',
        appclass=parser.KrDongaParser,
        appdomain='www.donga.com'
    ),
    118: AppConfig(
        appid=118,
        appname='118_ltn',
        appclass=parser.TwTalkParser,
        appdomain='talk.ltn.com.tw'
    ),
    119: AppConfig(
        appid=119,
        appname='119_idn',
        appclass=parser.TwIdnParser,
        appdomain='www.idn.com.tw'
    ),
    120: AppConfig(
        appid=120,
        appname='120_rti',
        appclass=parser.TwRtiParser,
        appdomain='www.rti.org.tw'
    ),
    121: AppConfig(
        appid=121,
        appname='121_chinatimes',
        appclass=parser.TwChinatimesParser,
        appdomain='www.chinatimes.com'
    ),
    122: AppConfig(
        appid=122,
        appname='122_bccnews',
        appclass=parser.TwBccnewsParser,
        appdomain='bccnews.com.tw'
    ),
    123: AppConfig(
        appid=123,
        appname='123_taiwannews',
        appclass=parser.TwTaiwannewsParser,
        appdomain='www.taiwannews.com.tw'
    ),
    124: AppConfig(
        appid=124,
        appname='124_eracom',
        appclass=parser.TwEracomParser,
        appdomain='www.eracom.com.tw'
    ),
    125: AppConfig(
        appid=125,
        appname='125_ftvnews',
        appclass=parser.TwFtvnewsParser,
        appdomain='www.ftvnews.com.tw'
    ),
    126: AppConfig(
        appid=126,
        appname='126_udn',
        appclass=parser.TwUdnParser,
        appdomain='udn.com'
    ),
    127: AppConfig(
        appid=127,
        appname='127_gpwb',
        appclass=parser.TwGpwbParser,
        appdomain='mna.gpwb.gov.tw'
    ),
    128: AppConfig(
        appid=128,
        appname='128_nownews',
        appclass=parser.TwNownewsParser,
        appdomain='www.nownews.com'
    ),
    129: AppConfig(
        appid=129,
        appname='129_cts',
        appclass=parser.TwNewsctsParser,
        appdomain='news.cts.com.tw'
    ),
    130: AppConfig(
        appid=130,
        appname='130_tvbs',
        appclass=parser.TwTvbsParser,
        appdomain='news.tvbs.com.tw'
    ),
    131: AppConfig(
        appid=131,
        appname='131_tnikkei',
        appclass=parser.JpNikkeiParser,
        appdomain='cn.nikkei.com'
    ),
    132: AppConfig(
        appid=132,
        appname='132_nhk',
        appclass=parser.JpNhkParser,
        appdomain='www3.nhk.or.jp'
    ),
    133: AppConfig(
        appid=133,
        appname='133_edition',
        appclass=parser.UsaEditionParser,
        appdomain='edition.cnn.com'
    ),
    134: AppConfig(
        appid=134,
        appname='134_vox',
        appclass=parser.UsaVoxParser,
        appdomain='www.vox.com'
    ),
    135: AppConfig(
        appid=135,
        appname='135_wenweipo',
        appclass=parser.HkWenweipoParser,
        appdomain='www.wenweipo.com'
    ),
    136: AppConfig(
        appid=136,
        appname='136_bloombergchina',
        appclass=parser.UsaBloombergchinaParser,
        appdomain='www.bloombergchina.com'
    ),
    137: AppConfig(
        appid=137,
        appname='137_nypost',
        appclass=parser.UsaNypostParser,
        appdomain='nypost.com'
    ),
    # 138: AppConfig(
    #     appid=138,
    #     appname='138_nypost',
    #     appclass=parser.UsnewsParser,
    #     appdomain='nypost.com'
    # ),
    139: AppConfig(
        appid=139,
        appname='139_chinese',
        appclass=parser.ChineseParser,
        appdomain='chinese.joins.com'
    ),
    140: AppConfig(
        appid=140,
        appname='140_chinese',
        appclass=parser.JoongangParser,
        appdomain='www.joongang.co.kr'
    ),
    # 142: AppConfig(
    #     appid=142,
    #     appname='142_iiss',
    #     appclass=parser.IissParser,
    #     appdomain='www.iiss.org'
    # ),
    143: AppConfig(
        appid=143,
        appname='143_pewresearch',
        appclass=parser.PewresearchParser,
        appdomain='www.pewresearch.org'
    ),
    144: AppConfig(
        appid=144,
        appname='144_hudson',
        appclass=parser.HudsonParser,
        appdomain='www.hudson.org'
    ),
    145: AppConfig(
        appid=145,
        appname='145_atlanticcouncil',
        appclass=parser.AtlanticcouncilParser,
        appdomain='www.atlanticcouncil.org'
    ),
    146: AppConfig(
        appid=146,
        appname='146_brookings',
        appclass=parser.BrookingsParser,
        appdomain='www.brookings.edu'
    ),
    147: AppConfig(
        appid=147,
        appname='147_project2049',
        appclass=parser.Project2049Parser,
        appdomain='project2049.net'
    ),
    148: AppConfig(
        appid=148,
        appname='148_wilsoncenter',
        appclass=parser.WilsoncenterParser,
        appdomain='www.wilsoncenter.org'
    ),
    149: AppConfig(
        appid=149,
        appname='149_understandingwar',
        appclass=parser.UnderstandingwarParser,
        appdomain='www.understandingwar.org'
    ),
    150: AppConfig(
        appid=150,
        appname='150_sejong',
        appclass=parser.KrSejongEnParser,
        appdomain='sejong.org/en'
    ),
    151: AppConfig(
        appid=151,
        appname='151_sejong',
        appclass=parser.KrSejongParser,
        appdomain='sejong.org/kr'
    ),
    153: AppConfig(
        appid=153,
        appname='153_president',
        appclass=parser.PresidentParser,
        appdomain='www.president.gov.tw'
    ),
    154: AppConfig(
        appid=154,
        appname='154_ey',
        appclass=parser.TwEyParser,
        appdomain='www.ey.gov.tw'
    ),
    155: AppConfig(
        appid=155,
        appname='155_mofa',
        appclass=parser.MofaParser,
        appdomain='www.mofa.gov.tw'
    ),
    156: AppConfig(
        appid=156,
        appname='156_pacom',
        appclass=parser.UsaPacomParser,
        appdomain='www.pacom.mil'
    ),
    157: AppConfig(
        appid=157,
        appname='157_army',
        appclass=parser.ArmyParser,
        appdomain='www.army.mil'
    ),
    158: AppConfig(
        appid=158,
        appname='158_navy',
        appclass=parser.UsaNavyarser,
        appdomain='www.navy.mil'
    ),
    159: AppConfig(
        appid=159,
        appname='159_state',
        appclass=parser.UsaStateParser,
        appdomain='www.state.gov'
    ),
    160: AppConfig(
        appid=160,
        appname='160_defense',
        appclass=parser.UsaDefenseParser,
        appdomain='www.defense.gov'
    ),
    161: AppConfig(
        appid=161,
        appname='161_dsca',
        appclass=parser.UsaDscaParser,
        appdomain='www.dsca.mil'
    ),
    162: AppConfig(
        appid=162,
        appname='162_jcs',
        appclass=parser.UsaJcsParser,
        appdomain='www.jcs.mil'
    ),
    163: AppConfig(
        appid=163,
        appname='163_taiwan',
        appclass=parser.TwTaiwanParser,
        appdomain='www.taiwan.cn'
    ),
    164: AppConfig(
        appid=164,
        appname='164_ctitv',
        appclass=parser.TwCtitvParser,
        appdomain='gotv.ctitv.com.tw'
    ),
    165: AppConfig(
        appid=165,
        appname='165_pssi',
        appclass=parser.CzPssiParser,
        appdomain='www.pssi.cz'
    ),
    166: AppConfig(
        appid=166,
        appname='166_tribune',
        appclass=parser.TribuneParser,
        appdomain='tribune.com.pk'
    ),
    167: AppConfig(
        appid=167,
        appname='167_straitstimes',
        appclass=parser.SgStraitstimesParser,
        appdomain='www.straitstimes.com'
    ),
    168: AppConfig(
        appid=168,
        appname='168_dhs',
        appclass=parser.UsaDhsParser,
        appdomain='www.dhs.gov'
    ),
    169: AppConfig(
        appid=169,
        appname='169_turkistan',
        appclass=parser.TrEastTurkistanParser,
        appdomain='east-turkistan.net'
    ),
    170: AppConfig(
        appid=170,
        appname='170_riss',
        appclass=parser.RuRissParser,
        appdomain='riss.ru'
    ),
    171: AppConfig(
        appid=171,
        appname='171_kremlin',
        appclass=parser.RukKemlinParser,
        appdomain='kremlin.ru'
    ),
    172: AppConfig(
        appid=172,
        appname='172_ctee',
        appclass=parser.TwCteeParser,
        appdomain='ctee.com.tw'
    ),
    173: AppConfig(
        appid=173,
        appname='173_tpof',
        appclass=parser.TwTpofParser,
        appdomain='www.tpof.org'
    ),
    174: AppConfig(
        appid=174,
        appname='174_formosa',
        appclass=parser.TwFormosaParser,
        appdomain='www.my-formosa.com'
    ),
    175: AppConfig(
        appid=175,
        appname='175_taiwanthinktank',
        appclass=parser.TwTaiwanthinktankParser,
        appdomain='www.taiwanthinktank.org'
    ),
    176: AppConfig(
        appid=176,
        appname='176_zmedia',
        appclass=parser.TwZmediaParser,
        appdomain='www.zmedia.com.tw'
    ),
    177: AppConfig(
        appid=177,
        appname='177_polls',
        appclass=parser.TwPollsParser,
        appdomain='www.polls.com.tw'
    ),
    178: AppConfig(
        appid=178,
        appname='178_justice',
        appclass=parser.UsaJusticeParser,
        appdomain='www.justice.gov'
    ),
    179: AppConfig(
        appid=179,
        appname='179_afmc',
        appclass=parser.UsaAfmcParser,
        appdomain='www.afmc.af.mil'
    ),
    180: AppConfig(
        appid=180,
        appname='180_whitehouse',
        appclass=parser.UsaWhitehouseParser,
        appdomain='www.whitehouse.gov'
    ),
    181: AppConfig(
        appid=181,
        appname='181_dia',
        appclass=parser.UsaDiaParser,
        appdomain='www.dia.mil'
    ),
    182: AppConfig(
        appid=182,
        appname='182_inss',
        appclass=parser.UsaInssParser,
        appdomain='inss.ndu.edu'
    ),
    183: AppConfig(
        appid=183,
        appname='183_commerce',
        appclass=parser.UsaCommerceParser,
        appdomain='www.commerce.gov'
    ),
    184: AppConfig(
        appid=184,
        appname='184_mofa',
        appclass=parser.JpMofaParser,
        appdomain='www.mofa.go.jp'
    ),
    185: AppConfig(
        appid=185,
        appname='185_mofa',
        appclass=parser.JpJfssParser,
        appdomain='www.mofa.go.jp'
    ),
    186: AppConfig(
        appid=186,
        appname='186_eai',
        appclass=parser.KrEaiParser,
        appdomain='www.eai.or.kr'
    ),
    187: AppConfig(
        appid=187,
        appname='187_ttv',
        appclass=parser.TwTtvParser,
        appdomain='news.ttv.com.tw'
    ),
    188: AppConfig(
        appid=188,
        appname='188_afpc',
        appclass=parser.UsaAfpcParser,
        appdomain='www.afpc.org'
    ),
    189: AppConfig(
        appid=189,
        appname='189_dphk',
        appclass=parser.HkDphkParser,
        appdomain='www.dphk.org'
    ),
    190: AppConfig(
        appid=190,
        appname='190_ccg',
        appclass=parser.CnCcgParser,
        appdomain='en.ccg.org.cn'
    ),
    191: AppConfig(
        appid=191,
        appname='191_mirrormedia',
        appclass=parser.TwMirrormediaParser,
        appdomain='www.mirrormedia.mg'
    ),
    192: AppConfig(
        appid=192,
        appname='192_upmedia',
        appclass=parser.TwUpmediaParser,
        appdomain='www.upmedia.mg'
    ),
    193: AppConfig(
        appid=193,
        appname='193_voicettank',
        appclass=parser.TwVoicettankParser,
        appdomain='voicettank.org'
    ),
    194: AppConfig(
        appid=194,
        appname='194_globalaffairs',
        appclass=parser.UsaGlobalaffairsParser,
        appdomain='globalaffairs.org'
    ),
    195: AppConfig(
        appid=195,
        appname='195_ctwant',
        appclass=parser.TwCtwantParser,
        appdomain='www.ctwant.com'
    ),
    196: AppConfig(
        appid=196,
        appname='196_tnr',
        appclass=parser.TwTnrParser,
        appdomain='tnr.com.tw'
    ),
    197: AppConfig(
        appid=197,
        appname='197_cier',
        appclass=parser.TwCierParser,
        appdomain='www.cier.edu.tw'
    ),
    198: AppConfig(
        appid=198,
        appname='198_kmt',
        appclass=parser.TwKmtParser,
        appdomain='www.kmt.org.tw'
    ),
    199: AppConfig(
        appid=199,
        appname='199_civilmedia',
        appclass=parser.TwCivilmediaParser,
        appdomain='www.civilmedia.tw'
    ),
    200: AppConfig(
        appid=200,
        appname='200_npa',
        appclass=parser.TwNpaParser,
        appdomain='www.npa.gov.tw'
    ),
    201: AppConfig(
        appid=201,
        appname='201_ettoday',
        appclass=parser.TwEttodayParser,
        appdomain='www.ettoday.net'
    ),
    202: AppConfig(
        appid=202,
        appname='202_peoplemedia',
        appclass=parser.TwPeoplemediaParser,
        appdomain='www.peoplemedia.tw'
    ),
    203: AppConfig(
        appid=203,
        appname='203_newtalk',
        appclass=parser.TwNewtalkParser,
        appdomain='newtalk.tw'
    ),
    204: AppConfig(
        appid=204,
        appname='204_mdnkids',
        appclass=parser.TwMdnkidsParser,
        appdomain='www.mdnkids.com'
    ),
    205: AppConfig(
        appid=205,
        appname='205_navy',
        appclass=parser.TwNavyMndParser,
        appdomain='navy.mnd.gov.tw'
    ),
    206: AppConfig(
        appid=206,
        appname='206_dppnff',
        appclass=parser.TwDppnffParser,
        appdomain='www.dppnff.tw'
    ),
    207: AppConfig(
        appid=207,
        appname='206_appledaily',
        appclass=parser.TwAppledailyParser,
        appdomain='tw.appledaily.com'
    ),
    208: AppConfig(
        appid=208,
        appname='208_dpp',
        appclass=parser.TwDppParser,
        appdomain='www.dpp.org.tw'
    ),
    209: AppConfig(
        appid=209,
        appname='209_ydn',
        appclass=parser.TwYdnParser,
        appdomain='www.ydn.com.tw'
    ),
    210: AppConfig(
        appid=210,
        appname='210_12371',
        appclass=parser.CN_12371Parser,
        appdomain='www.12371.cn'
    ),
    212: AppConfig(
        appid=212,
        appname='212_abcnews',
        appclass=parser.UsaAbcnewsParser,
        appdomain='abcnews.go.com'
    ),
    213: AppConfig(
        appid=213,
        appname='213_tw_ntpcgov',
        appclass=parser.TW_ntpcgovParser,
        appdomain='www.ntpc.gov.tw'
    ),
    214: AppConfig(
        appid=214,
        appname='214_tw_mnd',
        appclass=parser.TwMndParser,
        appdomain='www.mnd.gov.tw'
    ),
    215: AppConfig(
        appid=215,
        appname='215_news',
        appclass=parser.CnNewsParser,
        appdomain='www.news.cn'
    ),
    216: AppConfig(
        appid=216,
        appname='216_huanqiu',
        appclass=parser.CnHuanqiuParser,
        appdomain='www.huanqiu.com'
    ),
    217: AppConfig(
        appid=217,
        appname='217_chinanews',
        appclass=parser.CnChinanewsParser,
        appdomain='www.chinanews.com.cn'
    ),
    218: AppConfig(
        appid=218,
        appname='218_cankaoxiaoxi',
        appclass=parser.CnCankaoxiaoxiParser,
        appdomain='column.cankaoxiaoxi.com'
    ),
    219: AppConfig(
        appid=219,
        appname='219_chinausfocus',
        appclass=parser.CnChinausfocusParser,
        appdomain='cn.chinausfocus.com'
    ),
    220: AppConfig(
        appid=220,
        appname='220_stheadline',
        appclass=parser.HkStheadlineParser,
        appdomain='std.stheadline.com'
    ),
    221: AppConfig(
        appid=221,
        appname='221_cfisnet',
        appclass=parser.CnCfisnetParser,
        appdomain='news.cfisnet.com'
    ),
    222: AppConfig(
        appid=222,
        appname='222_mfa',
        appclass=parser.CnMfaParser,
        appdomain='www.mfa.gov.cn'
    ),
    223: AppConfig(
        appid=223,
        appname='223_haixia',
        appclass=parser.CnHaixiaParser,
        appdomain='haixia-info.com'
    ),
    224: AppConfig(
        appid=224,
        appname='224_hk01',
        appclass=parser.HkHk01Parser,
        appdomain='www.hk01.com'
    ),
    225: AppConfig(
        appid=225,
        appname='225_storm',
        appclass=parser.TwStormParser,
        appdomain='www.storm.mg'
    ),
    226: AppConfig(
        appid=226,
        appname='226_hani',
        appclass=parser.Kr_haniParser,
        appdomain='china.hani.co.kr'
    ),
    228: AppConfig(
        appid=228,
        appname='228_thepaper',
        appclass=parser.CnThepaperParser,
        appdomain='www.thepaper.cn'
    ),
    229: AppConfig(
        appid=229,
        appname='229_uscnpm',
        appclass=parser.CnUscnpmParser,
        appdomain='www.uscnpm.com'
    ),
    230: AppConfig(
        appid=230,
        appname='230_sinica',
        appclass=parser.TW_sinicaParser,
        appdomain='www.sinica.edu.tw'
    ),
    231: AppConfig(
        appid=231,
        appname='231_fsc',
        appclass=parser.TwFscParser,
        appdomain='www.fsc.gov.tw'
    ),
    232: AppConfig(
        appid=232,
        appname='232_ocac',
        appclass=parser.TwOcacParser,
        appdomain='www.ocac.gov.tw'
    ),
    233: AppConfig(
        appid=233,
        appname='233_vac',
        appclass=parser.TwVacParser,
        appdomain='www.vac.gov.tw'
    ),
    234: AppConfig(
        appid=234,
        appname='234_cec',
        appclass=parser.TwCecParser,
        appdomain='www.cec.gov.tw'
    ),
    236: AppConfig(
        appid=236,
        appname='236_nstc',
        appclass=parser.TwNstcParser,
        appdomain='www.nstc.gov.tw'
    ),
    237: AppConfig(
        appid=237,
        appname='237_npf',
        appclass=parser.TwNpfParser,
        appdomain='www.npf.org.tw'
    ),
    238: AppConfig(
        appid=238,
        appname='238_pfp',
        appclass=parser.TwPfpParser,
        appdomain='www.pfp.org.tw'
    ),
    239: AppConfig(
        appid=239,
        appname='239_np',
        appclass=parser.TwNpParser,
        appdomain='www.np.org.tw'
    ),
    240: AppConfig(
        appid=240,
        appname='240_np',
        appclass=parser.TwTppParser,
        appdomain='www.tpp.org.tw'
    ),
    241: AppConfig(
        appid=241,
        appname='241_mac',
        appclass=parser.TwMacParser,
        appdomain='www.mac.gov.tw'
    ),
    242: AppConfig(
        appid=242,
        appname='242_mac',
        appclass=parser.TwNcccParser,
        appdomain='www.ncc.gov.tw'
    ),
    243: AppConfig(
        appid=243,
        appname='243_epa',
        appclass=parser.TwEpaParser,
        appdomain='www.epa.gov.tw'
    ),
    244: AppConfig(
        appid=244,
        appname='244_epa',
        appclass=parser.TwCyParser,
        appdomain='www.cy.gov.tw'
    ),
    245: AppConfig(
        appid=245,
        appname='245_epa',
        appclass=parser.TwHakkaParser,
        appdomain='www.hakka.gov.tw'
    ),
    246: AppConfig(
        appid=246,
        appname='246_epa',
        appclass=parser.TwAecParser,
        appdomain='www.aec.gov.tw'
    ),
    247: AppConfig(
        appid=247,
        appname='247_matsu',
        appclass=parser.TwMatsuParser,
        appdomain='www.matsu.gov.tw'
    ),
    248: AppConfig(
        appid=248,
        appname='248_penghu',
        appclass=parser.TwPenghuParser,
        appdomain='www.penghu.gov.tw'
    ),
    249: AppConfig(
        appid=249,
        appname='249_mnd',
        appclass=parser.TwAirMndParser,
        appdomain='air.mnd.gov.tw'
    ),
    250: AppConfig(
        appid=250,
        appname='250_bcc',
        appclass=parser.TwBccParser,
        appdomain='www.bcc.com.tw'
    ),
    251: AppConfig(
        appid=251,
        appname='251_miaoli',
        appclass=parser.TwMiaoliParser,
        appdomain='www.miaoli.gov.tw'
    ),
    252: AppConfig(
        appid=252,
        appname='252_kcg',
        appclass=parser.TwKcgParser,
        appdomain='www.kcg.gov.tw'
    ),
    253: AppConfig(
        appid=253,
        appname='253_hk',
        appclass=parser.HkCcParser,
        appdomain='hk.on.cc'
    ),
    254: AppConfig(
        appid=254,
        appname='254_tainan',
        appclass=parser.TwTainanParser,
        appdomain='www.tainan.gov.tw'
    ),
    255: AppConfig(
        appid=255,
        appname='255_tainan',
        appclass=parser.TwJudicialParser,
        appdomain='www.judicial.gov.tw'
    ),
    256: AppConfig(
        appid=256,
        appname='256_tainan',
        appclass=parser.TwMoeaParser,
        appdomain='www.moea.gov.tw'
    ),
    257: AppConfig(
        appid=257,
        appname='257_tainan',
        appclass=parser.TwMoiParser,
        appdomain='www.moi.gov.tw'
    ),
    258: AppConfig(
        appid=258,
        appname='258_tainan',
        appclass=parser.TwTaipeiParser,
        appdomain='www.gov.taipei'
    ),
    259: AppConfig(
        appid=259,
        appname='259_tainan',
        appclass=parser.TwElandParser,
        appdomain='www.e-land.gov.tw'
    ),
    260: AppConfig(
        appid=260,
        appname='260_tainan',
        appclass=parser.TwAamacauParser,
        appdomain='aamacau.com'
    ),
    261: AppConfig(
        appid=261,
        appname='261_tainan',
        appclass=parser.PhPidsParser,
        appdomain='www.pids.gov.ph'
    ),
    262: AppConfig(
        appid=262,
        appname='262_tainan',
        appclass=parser.TwKinmenParser,
        appdomain='www.kinmen.gov.tw'
    ),
    # 风控
    # 263: AppConfig(
    #     appid=263,
    #     appname='263_philstar',
    #     appclass=parser.UsaPhilstarParser,
    #     appdomain='www.philstar.com'
    # ),
    264: AppConfig(
        appid=264,
        appname='264_gnlm',
        appclass=parser.MMGnlmParser,
        appdomain='www.gnlm.com.mm'
    ),
    265: AppConfig(
        appid=265,
        appname='265_zaobao',
        appclass=parser.SgZaobaoParser,
        appdomain='www.zaobao.com.sg'
    ),
    # 266: AppConfig(
    #     appid=266,
    #     appname='266_vakiodaily',
    #     appclass=parser.MoVakiodailyParser,
    #     appdomain='www.vakiodaily.com'
    # ),
    268: AppConfig(
        appid=268,
        appname='268_kyodo',
        appclass=parser.JpKyodoParser,
        appdomain='www.kyodo.co.jp'
    ),
    269: AppConfig(
        appid=269,
        appname='269_sgpc',
        appclass=parser.SgSgpcParser,
        appdomain='www.sgpc.gov.sg'
    ),
    270:AppConfig(
        appid=270,
        appname='270_spacecom',
        appclass=parser.UsaSpacecomParser,
        appdomain='www.spacecom.mil'
    ),
    271:AppConfig(
        appid=271,
        appname='271_thehindu',
        appclass=parser.IdThehinduParser,
        appdomain='www.thehindu.com'
    ),
    # 272:AppConfig(
    #     appid=272,
    #     appname='272_news',
    #     appclass=parser.AuNewsParser,
    #     appdomain='www.news.com.au'
    # ),
    273:AppConfig(
        appid=273,
        appname='273_snl24',
        appclass=parser.ZaSnl24Parser,
        appdomain='www.snl24.com'
    ),
    274:AppConfig(
        appid=274,
        appname='274_gvm',
        appclass=parser.TwGvmParser,
        appdomain='www.gvm.com.tw'
    ),
    275:AppConfig(
        appid=275,
        appname='275_chathamhouse',
        appclass=parser.UsaChathamhouseParser,
        appdomain='www.chathamhouse.org'
    ),
    276:AppConfig(
        appid=276,
        appname='276_forum',
        appclass=parser.JpForumParser,
        appdomain='www.t-i-forum.co.jp'
    ),
    277:AppConfig(
        appid=277,
        appname='277_jiia',
        appclass=parser.JpJiiaParser,
        appdomain='www.jiia.or.jp'
    ),
    278:AppConfig(
        appid=278,
        appname='278_defenseone',
        appclass=parser.UsaDefenseoneParser,
        appdomain='www.defenseone.com'
    ),
    279:AppConfig(
        appid=279,
        appname='279_csps',
        appclass=parser.BnCspsParser,
        appdomain='www.csps.a.bn'
    ),
    280:AppConfig(
        appid=280,
        appname='280_lockheedmartin',
        appclass=parser.UsaLockheedmartinParser,
        appdomain='news.lockheedmartin.com'
    ),
    281:AppConfig(
        appid=281,
        appname='281_caita',
        appclass=parser.TwCaitaParser,
        appdomain='www.caita.org.tw'
    ),
    282:AppConfig(
        appid=282,
        appname='282_atlasnetwork',
        appclass=parser.IdAtlAsnetworkParser,
        appdomain='www.atlasnetwork.org'
    ),
    283:AppConfig(
        appid=283,
        appname='283_acts',
        appclass=parser.IdActsParser,
        appdomain='www.acts-net.org'
    ),
    284:AppConfig(
        appid=284,
        appname='284_teriin',
        appclass=parser.IdTeriinParser,
        appdomain='www.teriin.org'
    ),
    285:AppConfig(
        appid=285,
        appname='285_cedice',
        appclass=parser.VeCediCeParser,
        appdomain='cedice.org.ve'
    ),
    286:AppConfig(
        appid=286,
        appname='286_ifwkiel',
        appclass=parser.DeIfwkIelParser,
        appdomain='www.ifw-kiel.de'
    ),
    287:AppConfig(
        appid=287,
        appname='287_potsdam',
        appclass=parser.DePotsdamParser,
        appdomain='www.pik-potsdam.de'
    ),
    288:AppConfig(
        appid=288,
        appname='288_guchusum1991',
        appclass=parser.XzGuchusum1991Parser,
        appdomain='en.guchusum1991.org'
    ),
    289:AppConfig(
        appid=289,
        appname='289_tibetexpress',
        appclass=parser.XzTibeTexpressParser,
        appdomain='tibetexpress.net'
    ),
    290:AppConfig(
        appid=290,
        appname='290_voakorea',
        appclass=parser.KrVoakoreaParser,
        appdomain='www.voakorea.com'
    ),
    291:AppConfig(
        appid=291,
        appname='291_usni',
        appclass=parser.UsaUsniParser,
        appdomain='news.usni.org'
    ),
    292:AppConfig(
        appid=292,
        appname='292_csbaonline',
        appclass=parser.UsaCsbaonlineParser,
        appdomain='csbaonline.org'
    ),
    293:AppConfig(
        appid=293,
        appname='293_baesystems',
        appclass=parser.UsaBaesystemsParser,
        appdomain='www.baesystems.com'
    ),
    294:AppConfig(
        appid=294,
        appname='294_airforce',
        appclass=parser.UsaAirforceParser,
        appdomain='www.airforce-technology.com'
    ),
    295:AppConfig(
        appid=295,
        appname='295_tisr',
        appclass=parser.TwTisrParser,
        appdomain='www.tisr.com.tw'
    ),
    296:AppConfig(
        appid=296,
        appname='296_army-technology',
        appclass=parser.UsaArmy_technologyParser,
        appdomain='www.army-technology.com'
    ),
    297:AppConfig(
        appid=297,
        appname='297_military',
        appclass=parser.UsaMilitaryParser,
        appdomain='www.military.com'
    ),
    298:AppConfig(
        appid=298,
        appname='298_aidc',
        appclass=parser.TwAidcParser,
        appdomain='www.aidc.com.tw'
    ),
    300:AppConfig(
        appid=300,
        appname='300_enanyang',
        appclass=parser.MyEnanyangParser,
        appdomain='www.enanyang.my'
    ),
    301:AppConfig(
        appid=301,
        appname='301_iseas',
        appclass=parser.SgIseasParser,
        appdomain='www.iseas.edu.sg'
    ),
    302:AppConfig(
        appid=302,
        appname='302_ateneo',
        appclass=parser.PhAteneoParser,
        appdomain='www.ateneo.edu'
    ),
    304:AppConfig(
        appid=304,
        appname='304_thechicagocouncil',
        appclass=parser.UsaThechicagocouncilParser,
        appdomain='www.thechicagocouncil.org'
    ),
    315:AppConfig(
        appid=315,
        appname='315_exteriores',
        appclass=parser.EsExterioresParser,
        appdomain='www.exteriores.gob.es'
    ),
    305:AppConfig(
        appid=305,
        appname='305_brudirect',
        appclass=parser.BN_brudirectParser,
        appdomain='www.brudirect.com'
    ),
    306:AppConfig(
        appid=306,
        appname='306_asaninst',
        appclass=parser.AsaninstParser,
        appdomain='www.asaninst.org'
    ),
    # 307:AppConfig(
    #     appid=307,
    #     appname='307_vientianetimeslao',
    #     appclass=parser.LaVientianetimeslaoParser,
    #     appdomain='www.vientianetimeslao.la'
    # ),
    308:AppConfig(
        appid=308,
        appname='308_kpl',
        appclass=parser.LaKplParser,
        appdomain='kpl.gov.la'
    ),
    309:AppConfig(
        appid=309,
        appname='309_nco',
        appclass=parser.KrNcoParser,
        appdomain='www.nco.mil.kr'
    ),
    310:AppConfig(
        appid=310,
        appname='310_cup',
        appclass=parser.HkCupParser,
        appdomain='www.cup.com.hk'
    ),
    311:AppConfig(
        appid=311,
        appname='311_c7f',
        appclass=parser.UsaC7fParser,
        appdomain='www.c7f.navy.mil'
    ),
    312:AppConfig(
        appid=312,
        appname='312_kdi',
        appclass=parser.KrKdiParser,
        appdomain='www.kdi.re.kr'
    ),
    313:AppConfig(
        appid=313,
        appname='313_sei',
        appclass=parser.UsaSeiParser,
        appdomain='www.sei.cmu.edu'
    ),
    314:AppConfig(
        appid=314,
        appname='314_fpri',
        appclass=parser.UsaFpriParser,
        appdomain='www.fpri.org'
    ),
    316:AppConfig(
        appid=316,
        appname='316_ryomyong',
        appclass=parser.KrRyomyongParser,
        appdomain='www.ryomyong.com'
    ),
    317:AppConfig(
        appid=317,
        appname='317_newsMn',
        appclass=parser.MnNewsMNParser,
        appdomain='news.mn'
    ),
    318:AppConfig(
        appid=318,
        appname='318_theubposts',
        appclass=parser.MnTheubposTsParser,
        appdomain='theubposts.com'
    ),
    319:AppConfig(
        appid=319,
        appname='319_mongoliaweekly',
        appclass=parser.MnMongoliaweeklyParser,
        appdomain='www.mongoliaweekly.org'
    ),
    320:AppConfig(
        appid=320,
        appname='320_dnn',
        appclass=parser.MnDnnParser,
        appdomain='dnn.mn'
    ),
    3002: AppConfig(
        appid=3002,
        appname='3002_ec-europa',
        appclass=parser.EcEuropaParser,
        appdomain='ec.europa.eu'
    ),
    3003: AppConfig(
        appid=3003,
        appname='3003_cnic',
        appclass=parser.CNICParser,
        appdomain='www.cnic.navy.mil'
    ),
    3004: AppConfig(
        appid=3004,
        appname='3004_cecgov',
        appclass=parser.CecgovParser,
        appdomain='www.cec.gov.tw'
    ),
    3005: AppConfig(
        appid=3005,
        appname='3005_krarmymil',
        appclass=parser.KrarmymilParser,
        appdomain='army.mil.kr'
    ),
    3006: AppConfig(
        appid=3006,
        appname='3006_navalsafetycenter',
        appclass=parser.UsanavalsafetycenterParser,
        appdomain='navalsafetycenter.navy.mil'
    ),
    1005: AppConfig(
        appid=1005,
        appname='1005_ru_government',
        appclass=parser.Ru_govermentParser,
        appdomain='government.ru'
    ),
    1006: AppConfig(
        appid=1006,
        appname='1006_ru_scrfgov',
        appclass=parser.Ru_scrfgovParser,
        appdomain='www.scrf.gov.ru'
    ),
    1007: AppConfig(
        appid=1007,
        appname='1007_tw_nccuedu',
        appclass=parser.Tw_nccueduParser,
        appdomain='iir.nccu.edu.tw'
    ),
    1008: AppConfig(
        appid=1008,
        appname='1008_tw_itriorg',
        appclass=parser.Tw_itriorgParser,
        appdomain='www.itri.org.tw'
    ),
    1009: AppConfig(
        appid=1009,
        appname='1009_usa_amlcarmy',
        appclass=parser.Usa_amlcarmyParser,
        appdomain='www.amlc.army.mil'
    ),
    1010: AppConfig(
        appid=1010,
        appname='1010_usa_usma',
        appclass=parser.USA_usmaParser,
        appdomain='digital-library.usma.edu'
    ),
    2007: AppConfig(
        appid=2007,
        appname='2007_12ftwaf',
        appclass=parser.Usa_12ftw_afParser,
        appdomain='www.12ftw.af.mil'
    ),
    2008: AppConfig(
        appid=2008,
        appname='2008_2idkoreaarmy',
        appclass=parser.Usa_2idkorea_armyParser,
        appdomain='www.2id.korea.army.mil'
    ),
    2009: AppConfig(
        appid=2009,
        appname='2009_afneurope',
        appclass=parser.Usa_afneuropeParser,
        appdomain='www.afneurope.net'
    ),
    2010: AppConfig(
        appid=2010,
        appname='2010_afnpacific',
        appclass=parser.Usa_afnpacificParser,
        appdomain='www.afnpacific.net'
    ),
    2011: AppConfig(
        appid=2011,
        appname='2011_afrc_afmil',
        appclass=parser.Usa_afrc_afmilParser,
        appdomain='www.afrc.af.mil'
    ),
    2012: AppConfig(
        appid=2012,
        appname='2012_airforcespecialtactics',
        appclass=parser.Usa_airforcespecialtacticsParser,
        appdomain='www.airforcespecialtactics.af.mil'
    ),
    2013: AppConfig(
        appid=2013,
        appname='2013_ang_afmil',
        appclass=parser.Usa_ang_afmilParser,
        appdomain='www.ang.af.mil'
    ),
    3007: AppConfig(
        appid=3007,
        appname='3007_usa_dcng_mil',
        appclass=parser.DcngmilParser,
        appdomain='dc.ng.mil'
    ),
    3008: AppConfig(
        appid=3008,
        appname='3008_usa_allhands',
        appclass=parser.AllhandsParser,
        appdomain='allhands.navy.mil'
    ),
    2014: AppConfig(
        appid=2014,
        appname='2014_navfac_navyafmil',
        appclass=parser.Usa_navfac_navymilParser,
        appdomain='www.navfac.navy.mil'
    ),
    2015: AppConfig(
        appid=2015,
        appname='2015_navsea_navyafmil',
        appclass=parser.Usa_navsea_navymilParser,
        appdomain='www.navsea.navy.mil'
    ),
    2016: AppConfig(
        appid=2016,
        appname='2016_navsea_navyafmil',
        appclass=parser.Kr_kima_reParser,
        appdomain='www.kima.re.kr'
    ),
    3009: AppConfig(
        appid=3009,
        appname='3009_usa_mcbhawaii',
        appclass=parser.McbhawaiiParser,
        appdomain='www.mcbhawaii.marines.mil'
    ),
    3010: AppConfig(
        appid=3010,
        appname='3010_usa_mcasfutenma',
        appclass=parser.McasfutenmaParser,
        appdomain='www.mcasfutenma.marines.mil'
    ),
    3011: AppConfig(
        appid=3011,
        appname='3011_usa_hillaf',
        appclass=parser.HillafParser,
        appdomain='www.hill.af.mil'
    ),
    3012: AppConfig(
        appid=3012,
        appname='3012_usa_europeafrica',
        appclass=parser.EuropeafricaParser,
        appdomain='www.europeafrica.army.mil'
    ),
    3013: AppConfig(
        appid=3013,
        appname='3013_usa_cnatra',
        appclass=parser.CnatraParser,
        appdomain='www.cnatra.navy.mil'
    ),
    3014: AppConfig(
        appid=3014,
        appname='3014_usa_psmagazine',
        appclass=parser.PsmagazineParser,
        appdomain='www.psmagazine.army.mil'
    ),
    3015: AppConfig(
        appid=3015,
        appname='3015_usa_arnortharmy',
        appclass=parser.ArnorthArmyParser,
        appdomain='www.arnorth.army.mil'
    ),
    3016: AppConfig(
        appid=3016,
        appname='3016_usa_armywarcollege',
        appclass=parser.ArmywarcollegeParser,
        appdomain='www.armywarcollege.edu'
    ),
    3017: AppConfig(
        appid=3017,
        appname='3017_usa_ncisnavy',
        appclass=parser.NcisnavyParser,
        appdomain='www.ncis.navy.mil'
    ),
    3018: AppConfig(
        appid=3018,
        appname='3018_usa_oregon',
        appclass=parser.OregonParser,
        appdomain='www.oregon.gov'
    ),
    # 3019: AppConfig(
    #     appid=3019,
    #     appname='3019_by_mfagov',
    #     appclass=parser.MfagovParser,
    #     appdomain='www.mfa.gov.by'
    # ),
    3020: AppConfig(
        appid=3020,
        appname='3020_by_economy',
        appclass=parser.EconomyParser,
        appdomain='www.economy.gov.by'
    ),
    3021: AppConfig(
        appid=3021,
        appname='3021_usa_rfforg',
        appclass=parser.RfforgParser,
        appdomain='www.rff.org'
    ),
    3022: AppConfig(
        appid=3022,
        appname='3022_usa_gmfus',
        appclass=parser.GmfusParser,
        appdomain='www.gmfus.org'
    ),
    3023: AppConfig(
        appid=3023,
        appname='3023_usa_nberorg',
        appclass=parser.NberorgParser,
        appdomain='www.nber.org'
    ),
    3024: AppConfig(
        appid=3024,
        appname='3024_usa_thedialogue',
        appclass=parser.ThedialogueParser,
        appdomain='www.thedialogue.org'
    ),
    2021: AppConfig(
        appid=2021,
        appname='2021_usa_spaceforce',
        appclass=parser.USA_spaceforceParser,
        appdomain='www.spaceforce.mil'
    ),
    2022: AppConfig(
        appid=2022,
        appname='2022_usa_army_mil',
        appclass=parser.USA_army_milParser,
        appdomain='www.army.mil'
    ),
    2023: AppConfig(
        appid=2023,
        appname='2023_usa_setaf_africa',
        appclass=parser.USA_setaf_africaParser,
        appdomain='www.setaf-africa.army.mil'
    ),
    2024: AppConfig(
        appid=2024,
        appname='2024_kr_narsgo',
        appclass=parser.KR_narsgoParser,
        appdomain='www.nars.go.kr'
    ),
    2025: AppConfig(
        appid=2025,
        appname='2025_kr_kidare',
        appclass=parser.KR_kidareParser,
        appdomain='www.kida.re.kr'
    ),
    2026: AppConfig(
        appid=2026,
        appname='2026_usa_visionofhumanity',
        appclass=parser.USA_visionofhumanityParser,
        appdomain='www.visionofhumanity.org'
    ),
    2027: AppConfig(
        appid=2027,
        appname='2027_jp_cnnco',
        appclass=parser.JP_cnncoSiteParser,
        appdomain='www.cnn.co.jp'
    ),
    2028: AppConfig(
        appid=2028,
        appname='2028_jp_japantimes',
        appclass=parser.JP_japantimesParser,
        appdomain='www.japantimes.co.jp'
    ),
    2029: AppConfig(
        appid=2029,
        appname='2029_usa_fortune',
        appclass=parser.USA_fortuneParser,
        appdomain='fortune.com'
    ),
    2030: AppConfig(
        appid=2030,
        appname='2030_ph_inquirer',
        appclass=parser.PH_inquirerParser,
        appdomain='newsinfo.inquirer.net'
    ),
    2031: AppConfig(
        appid=2031,
        appname='2031_ph_asianjournal',
        appclass=parser.PH_asianjournalParser,
        appdomain='www.asianjournal.com'
    ),
    2032: AppConfig(
        appid=2032,
        appname='2032_kr_news_kbs',
        appclass=parser.KR_news_kbsParser,
        appdomain='news.kbs.co.kr'
    ),
    2033: AppConfig(
        appid=2033,
        appname='2033_de_tonline',
        appclass=parser.DE_tonlineParser,
        appdomain='www.t-online.de'
    ),
    2034: AppConfig(
        appid=2034,
        appname='2034_ru_apn',
        appclass=parser.RU_apnParser,
        appdomain='www.apn.ru'
    ),
    2035: AppConfig(
        appid=2035,
        appname='2035_ru_ria',
        appclass=parser.RU_riaParser,
        appdomain='ria.ru'
    ),
    2036: AppConfig(
        appid=2036,
        appname='2036_ru_lenta',
        appclass=parser.RU_lentaParser,
        appdomain='lenta.ru'
    ),
    2037: AppConfig(
        appid=2037,
        appname='2037_ru_rbc',
        appclass=parser.RU_rbcParser,
        appdomain='www.rbc.ru'
    ),
    2038: AppConfig(
        appid=2038,
        appname='2038_sg_asiaone',
        appclass=parser.SG_asiaoneParser,
        appdomain='www.asiaone.com'
    ),
    2039: AppConfig(
        appid=2039,
        appname='2039_in_oneindia',
        appclass=parser.IN_oneindiaParser,
        appdomain='www.oneindia.com'
    ),
    2040: AppConfig(
        appid=2040,
        appname='2040_au_afr',
        appclass=parser.AU_afrParser,
        appdomain='www.afr.com'
    ),
    2041: AppConfig(
        appid=2041,
        appname='2041_br_folhauol',
        appclass=parser.BR_folhauolParser,
        appdomain='www1.folha.uol.com.br'
    ),
    2042: AppConfig(
        appid=2042,
        appname='2042_my_bernama',
        appclass=parser.MY_bernamaParser,
        appdomain='www.bernama.com'
    ),
    2043: AppConfig(
        appid=2043,
        appname='2043_kz_kazpravda',
        appclass=parser.KZ_kazpravdaParser,
        appdomain='kazpravda.kz'
    ),
    2044: AppConfig(
        appid=2044,
        appname='2044_ar_lacapital',
        appclass=parser.AR_lacapitalParser,
        appdomain='www.lacapital.com.ar'
    ),
    2045: AppConfig(
        appid=2045,
        appname='2045_lk_dailynews',
        appclass=parser.LK_dailynewsParser,
        appdomain='www.dailynews.lk'
    ),
    2046: AppConfig(
        appid=2046,
        appname='2046_ch_tagesanzeiger',
        appclass=parser.CH_tagesanzeigerParser,
        appdomain='www.tagesanzeiger.ch'
    ),
    2047: AppConfig(
        appid=2047,
        appname='2047_fr_euronews',
        appclass=parser.FR_euronewsParser,
        appdomain='www.euronews.com'
    ),
    2048: AppConfig(
        appid=2048,
        appname='2048_th_mfago',
        appclass=parser.TH_mfagoParser,
        appdomain='www.mfa.go.th'
    ),
    2049: AppConfig(
        appid=2049,
        appname='2049_sg_mfagov',
        appclass=parser.SG_mfagovParser,
        appdomain='www.mfa.gov.sg'
    ),
    2050: AppConfig(
        appid=2050,
        appname='2050_in_meagov',
        appclass=parser.IN_meagovParser,
        appdomain='www.mea.gov.in'
    ),
    2051: AppConfig(
        appid=2051,
        appname='2051_tr_mfagov',
        appclass=parser.TR_mfagovParser,
        appdomain='www.mfa.gov.tr'
    ),
    2052: AppConfig(
        appid=2052,
        appname='2052_rs_mfagov',
        appclass=parser.RS_mfagovParser,
        appdomain='www.mfa.gov.rs'
    ),
    2053: AppConfig(
        appid=2053,
        appname='2053_bt_mfagov',
        appclass=parser.BT_mfagovParser,
        appdomain='www.mfa.gov.bt'
    ),
    2054: AppConfig(
        appid=2054,
        appname='2054_gh_mfagov',
        appclass=parser.GH_mfagovParser,
        appdomain='mfa.gov.gh'
    ),
    2055: AppConfig(
        appid=2055,
        appname='2055_lk_mfagov',
        appclass=parser.LK_mfagovParser,
        appdomain='mfa.gov.lk'
    ),
    2056: AppConfig(
        appid=2056,
        appname='2056_so_mfagov',
        appclass=parser.SO_mfagovParser,
        appdomain='www.mfa.gov.so'
    ),
    2057: AppConfig(
        appid=2057,
        appname='2057_bh_mofagov',
        appclass=parser.BH_mofagovParser,
        appdomain='www.mofa.gov.bh'
    ),
    2058: AppConfig(
        appid=2058,
        appname='2058_de_auswaertiges_amt',
        appclass=parser.DE_auswaertigesParser,
        appdomain='www.auswaertiges-amt.de'
    ),
    2059: AppConfig(
        appid=2059,
        appname='2059_it_esteri',
        appclass=parser.IT_esteriParser,
        appdomain='www.esteri.it'
    ),
    2060: AppConfig(
        appid=2060,
        appname='2060_pt_portaldiplomatico',
        appclass=parser.PT_portaldiplomaticoParser,
        appdomain='portaldiplomatico.mne.gov.pt'
    ),
    2061: AppConfig(
        appid=2061,
        appname='2061_nl_government',
        appclass=parser.NL_governmentParser,
        appdomain='www.government.nl'
    ),
    2062: AppConfig(
        appid=2062,
        appname='2062_sg_sgpcgov',
        appclass=parser.SG_sgpcgovParser,
        appdomain='www.sgpc.gov.sg'
    ),
    2063: AppConfig(
        appid=2063,
        appname='2063_sg_gov',
        appclass=parser.SG_govParser,
        appdomain='www.gov.sg'
    ),
    2064: AppConfig(
        appid=2064,
        appname='2064_th_navymi',
        appclass=parser.TH_navymiParser,
        appdomain='www.navy.mi.th'
    ),
    2065: AppConfig(
        appid=2065,
        appname='2065_kr_airforcemil',
        appclass=parser.KR_airforcemilParser,
        appdomain='www.airforce.mil.kr'
    ),
    2066: AppConfig(
        appid=2066,
        appname='2066_ca_canada',
        appclass=parser.CA_canadaParser,
        appdomain='www.canada.ca'
    ),
    2067: AppConfig(
        appid=2067,
        appname='2067_dk_forsvaret',
        appclass=parser.DK_forsvaretParser,
        appdomain='www.forsvaret.dk'
    ),
    2068: AppConfig(
        appid=2068,
        appname='2068_is_lhg',
        appclass=parser.IS_lhgParser,
        appdomain='www.lhg.is'
    ),
    2069: AppConfig(
        appid=2069,
        appname='2069_is_logreglan',
        appclass=parser.IS_logreglanParser,
        appdomain='www.logreglan.is'
    ),
    2070: AppConfig(
        appid=2070,
        appname='2070_usa_voanews',
        appclass=parser.UsavoanewsParser,
        appdomain='www.voanews.com'
    ),
    2071: AppConfig(
        appid=2071,
        appname='2071_uk_bbc',
        appclass=parser.UkbbcParser,
        appdomain='www.bbc.com/zh'
    ),
    2072: AppConfig(
        appid=2072,
        appname='2072_uk_bbcen',
        appclass=parser.UkbbcenParser,
        appdomain='www.bbc.com/en'
    ),
    2073: AppConfig(
        appid=2073,
        appname='2073_cn_helanonline',
        appclass=parser.CnhelanonlineParser,
        appdomain='helanonline.cn'
    ),
    2074: AppConfig(
        appid=2074,
        appname='2074_ru_sputniknews',
        appclass=parser.RusputniknewsParser,
        appdomain='sputniknews.cn'
    ),
    2075: AppConfig(
        appid=2075,
        appname='2075_jp_chinakyodonews',
        appclass=parser.JpchinakyodonewsParser,
        appdomain='china.kyodonews.net'
    ),
    2076: AppConfig(
        appid=2076,
        appname='2076_tw_stnncc',
        appclass=parser.TW_stnnccParser,
        appdomain='www.stnn.cc'
    ),
    2077: AppConfig(
        appid=2077,
        appname='2077_tw_indsrorg',
        appclass=parser.TW_indsrorgParser,
        appdomain='indsr.org.tw'
    ),
    2078: AppConfig(
        appid=2078,
        appname='2078_hk_crntt',
        appclass=parser.HK_crnttParser,
        appdomain='hk.crntt.com'
    ),
    2079: AppConfig(
        appid=2079,
        appname='2079_cn_81',
        appclass=parser.CN_81Parser,
        appdomain='www.81.cn'
    ),
    2081: AppConfig(
        appid=2081,
        appname='2081_kr_tvdemamil',
        appclass=parser.KR_tvdemamilParser,
        appdomain='tv.dema.mil.kr'
    ),
    2082: AppConfig(
        appid=2082,
        appname='2082_jp_newsgoo',
        appclass=parser.JP_newsgooParser,
        appdomain='news.goo.ne.jp'
    ),
    2083: AppConfig(
        appid=2083,
        appname='2083_kr_ifansgo',
        appclass=parser.KR_ifransgoParser,
        appdomain='www.ifans.go.kr'
    ),
    2084: AppConfig(
        appid=2084,
        appname='2084_usa_washingtoninstitute',
        appclass=parser.USA_washingtoninstituteParser,
        appdomain='www.washingtoninstitute.org'
    ),
    2085: AppConfig(
        appid=2085,
        appname='2085_my_malaysian_chinese',
        appclass=parser.MY_malaysian_chineseParser,
        appdomain='www.malaysian-chinese.net'
    ),
    2086: AppConfig(
        appid=2086,
        appname='2086_in_indiafoundation',
        appclass=parser.IN_indiafoundationParser,
        appdomain='indiafoundation.in'
    ),
    2087: AppConfig(
        appid=2087,
        appname='2087_jp_kanteigo',
        appclass=parser.JP_kanteigoParser,
        appdomain='www.kantei.go.jp'
    ),
    2088: AppConfig(
        appid=2088,
        appname='2088_hk_insight',
        appclass=parser.HK_insightParser,
        appdomain='www.master-insight.com'
    ),
    2089: AppConfig(
        appid=2089,
        appname='2089_hk_takungpao',
        appclass=parser.HK_takungpaoParser,
        appdomain='www.takungpao.com'
    ),
    2090: AppConfig(
        appid=2090,
        appname='2090_hk_bastillepost',
        appclass=parser.HK_bastillepostParser,
        appdomain='www.bastillepost.com'
    ),
    2092: AppConfig(
        appid=2092,
        appname='2092_hk_newsnow',
        appclass=parser.HK_newsnowParser,
        appdomain='news.now.com'
    ),
    2093: AppConfig(
        appid=2093,
        appname='2093_vn_vietnamplus',
        appclass=parser.VN_vietnamplus,
        appdomain='zh.vietnamplus.vn'
    ),
    2094: AppConfig(
        appid=2094,
        appname='2094_kr_puacgo',
        appclass=parser.KR_puacgoParser,
        appdomain='www.puac.go.kr'
    ),
    2095: AppConfig(
        appid=2095,
        appname='2095_kr_ynaco',
        appclass=parser.KR_ynacoParser,
        appdomain='www.yna.co.kr'
    ),
    2096: AppConfig(
        appid=2096,
        appname='2095_xz_tibetsun',
        appclass=parser.XZ_tibetsunParser,
        appdomain='www.tibetsun.com'
    ),
    2097: AppConfig(
        appid=2097,
        appname='2097_in_icwa',
        appclass=parser.IN_icwaParser,
        appdomain='www.icwa.in'
    ),
    2098: AppConfig(
        appid=2098,
        appname='2098_capsindia',
        appclass=parser.IN_capsindiaParser,
        appdomain='capsindia.org'
    ),
    2099: AppConfig(
        appid=2099,
        appname='2099_delhipolicygroup',
        appclass=parser.IN_delhipolicygroupParser,
        appdomain='www.delhipolicygroup.org'
    ),
    2100: AppConfig(
        appid=2100,
        appname='2100_stimson',
        appclass=parser.USA_stimsonParser,
        appdomain='www.stimson.org'
    ),
    2101: AppConfig(
        appid=2101,
        appname='2101_my_isis',
        appclass=parser.MY_isisParser,
        appdomain='www.isis.org.my'
    ),
    2102: AppConfig(
        appid=2102,
        appname='2102_hk_mingpao',
        appclass=parser.HK_mingpaoParser,
        appdomain='news.mingpao.com'
    ),
    2104: AppConfig(
        appid=2104,
        appname='2104_kp_dailynk',
        appclass=parser.KP_dailynkParser,
        appdomain='www.dailynk.com'
    ),
    2105: AppConfig(
        appid=2105,
        appname='2105_kr_cnynaco',
        appclass=parser.KR_cnynacoParser,
        appdomain='cn.yna.co.kr'
    ),
    2106: AppConfig(
        appid=2106,
        appname='2106_jp_nidsmod',
        appclass=parser.JP_nidsmodParser,
        appdomain='www.nids.mod.go.jp'
    ),
    2107: AppConfig(
        appid=2107,
        appname='2107_in_jagran',
        appclass=parser.IN_jagranParser,
        appdomain='www.jagran.com'
    ),
    2108: AppConfig(
        appid=2108,
        appname='2108_id_thejakartapost',
        appclass=parser.ID_thejakartapost,
        appdomain='www.thejakartapost.com'
    ),
    2109: AppConfig(
        appid=2109,
        appname='2109_ph_new_inquire',
        appclass=parser.PH_new_inquirerParser,
        appdomain='globalnation.inquirer.net'  # 此网站域名为 newsinfo.inquirer.net   存在相同的
    ),
    2110: AppConfig(
        appid=2110,
        appname='2110_kr_mndgo',
        appclass=parser.KR_mndgoParser,
        appdomain='mnd.go.kr'
    ),
    2111: AppConfig(
        appid=2111,
        appname='2111_ru_globalaffairs',
        appclass=parser.RU_globalaffairsParser,
        appdomain='globalaffairs.ru'
    ),
    2112: AppConfig(
        appid=2112,
        appname='2112_ru_nvong',
        appclass=parser.RU_nvongParser,
        appdomain='nvo.ng.ru'
    ),
    2113: AppConfig(
        appid=2113,
        appname='2113_ru_vpknews',
        appclass=parser.RU_vpknewsParser,
        appdomain='vpk-news.ru'
    ),
    2114: AppConfig(
        appid=2114,
        appname='2114_th_bangkokpost',
        appclass=parser.TH_bangkokpostParser,
        appdomain='www.bangkokpost.com'
    ),
    2115: AppConfig(
        appid=2115,
        appname='2115_th_udnbkk',
        appclass=parser.TH_udnbkkParser,
        appdomain='www.udnbkk.com'
    ),
    2116: AppConfig(
        appid=2116,
        appname='2116_th_dailynewsco',
        appclass=parser.TH_dailynewscoParser,
        appdomain='www.dailynews.co.th'
    ),
    2117: AppConfig(
        appid=2117,
        appname='2117_my_sinchew',
        appclass=parser.MY_sinchewParser,
        appdomain='www.sinchew.com.my'
    ),
    2118: AppConfig(
        appid=2118,
        appname='2118_mo_waou',
        appclass=parser.MO_waouParser,
        appdomain='www.waou.com.mo'
    ),
    2119: AppConfig(
        appid=2119,
        appname='2119_kh_jianhuadaily',
        appclass=parser.KH_jianhuadailyParser,
        appdomain='jianhuadaily.com'
    ),
    2120: AppConfig(
        appid=2120,
        appname='2120_cdriorg',
        appclass=parser.KH_cdriorgParser,
        appdomain='cdri.org.kh'
    ),
    2121: AppConfig(
        appid=2121,
        appname='2121_tw_taiwandaily',
        appclass=parser.TW_taiwandailyParser,
        appdomain='www.taiwandaily.net'
    ),
    2122: AppConfig(
        appid=2122,
        appname='2122_in_idsa',
        appclass=parser.IN_idsaParser,
        appdomain='www.idsa.in'
    ),
    2123: AppConfig(
        appid=2123,
        appname='2123_sg_channelnewsasia',
        appclass=parser.SgChannelnewsasiaParser,
        appdomain='www.channelnewsasia.com'
    ),
    # 2124: AppConfig(
    #     appid=2124,
    #     appname='2124_kr_immigration',
    #     appclass=parser.KR_immigrationParser,
    #     appdomain='www.immigration.go.kr'
    # ),
    2125: AppConfig(
        appid=2125,
        appname='2125_kr_hikorea',
        appclass=parser.KR_hikoreaParser,
        appdomain='www.hikorea.go.kr'
    ),
    2126: AppConfig(
        appid=2126,
        appname='2126_jp_mojgo',
        appclass=parser.JP_mojgoParser,
        appdomain='www.moj.go.jp'
    ),
    3025: AppConfig(
        appid=3025,
        appname='3025_id_ncaer',
        appclass=parser.NcaerParser,
        appdomain='www.ncaer.org'
    ),
    3026: AppConfig(
        appid=3026,
        appname='3026_eu_isseuropa',
        appclass=parser.IsseuropaParser,
        appdomain='www.iss.europa.eu'
    ),
    3027: AppConfig(
        appid=3027,
        appname='3027_jp_newsdig',
        appclass=parser.NewsdigParser,
        appdomain='newsdig.tbs.co.jp'
    ),
    3028: AppConfig(
        appid=3028,
        appname='3028_usa_theatlantic',
        appclass=parser.TheatlanticParser,
        appdomain='www.theatlantic.com'
    ),
    3029: AppConfig(
        appid=3029,
        appname='3029_tw_timeshinet',
        appclass=parser.TimeshinetParser,
        appdomain='times.hinet.net'
    ),
    3030: AppConfig(
        appid=3030,
        appname='3030_uk_theguardian',
        appclass=parser.TheguardianParser,
        appdomain='www.theguardian.com'
    ),
    3031: AppConfig(
        appid=3031,
        appname='3031_uk_spectator',
        appclass=parser.SpectatorParser,
        appdomain='www.spectator.co.uk'
    ),
    3032: AppConfig(
        appid=3032,
        appname='3032_uk_newstatesman',
        appclass=parser.NewstatesmanParser,
        appdomain='www.newstatesman.com'
    ),
    3033: AppConfig(
        appid=3033,
        appname='3033_kr_etoday',
        appclass=parser.EtodayParser,
        appdomain='www.etoday.co.kr'
    ),
    3034: AppConfig(
        appid=3034,
        appname='3034_kr_ohmynews',
        appclass=parser.OhmynewsParser,
        appdomain='www.ohmynews.com'
    ),
    3035: AppConfig(
        appid=3035,
        appname='3035_usa_africom',
        appclass=parser.AfricomParser,
        appdomain='www.africom.mil'
    ),
    3036: AppConfig(
        appid=3036,
        appname='3036_ru_kpru',
        appclass=parser.KpruParser,
        appdomain='www.kp.ru'
    ),
    3037: AppConfig(
        appid=3037,
        appname='3037_ru_gazeta',
        appclass=parser.GazetaParser,
        appdomain='www.gazeta.ru'
    ),
    3038: AppConfig(
        appid=3038,
        appname='3038_ru_e1ru',
        appclass=parser.E1ruParser,
        appdomain='www.e1.ru'
    ),
    3039: AppConfig(
        appid=3039,
        appname='3039_tz_thecitizen',
        appclass=parser.ThecitizenParser,
        appdomain='www.thecitizen.co.tz'
    ),
    3040: AppConfig(
        appid=3040,
        appname='3040_vn_vovvn',
        appclass=parser.VovvnParser,
        appdomain='vov.vn'
    ),
    3041: AppConfig(
        appid=3041,
        appname='3041_pk_jang',
        appclass=parser.JangParser,
        appdomain='jang.com.pk'
    ),
    3042: AppConfig(
        appid=3042,
        appname='3042_mm_myanmarload',
        appclass=parser.MyanmarloadParser,
        appdomain='myanmarload.com'
    ),
    3043: AppConfig(
        appid=3043,
        appname='3043_et_waltainfo',
        appclass=parser.WaltainfoParser,
        appdomain='waltainfo.com'
    ),
    3044: AppConfig(
        appid=3044,
        appname='3044_ve_eluniversal',
        appclass=parser.EluniversalParser,
        appdomain='www.eluniversal.com'
    ),
    3045: AppConfig(
        appid=3045,
        appname='3045_usa_cookpolitical',
        appclass=parser.CookpoliticalParser,
        appdomain='www.cookpolitical.com'
    ),
    2017: AppConfig(
        appid=2017,
        appname='2017_ru_carnegie',
        appclass=parser.RU_carnegieParser,
        appdomain='carnegie.ru'
    ),
    2018: AppConfig(
        appid=2018,
        appname='2018_in_claws',
        appclass=parser.IN_clawsParser,
        appdomain='www.claws.in'
    ),
    2019: AppConfig(
        appid=2019,
        appname='2019_in_claws',
        appclass=parser.KR_korvaorParser,
        appdomain='www.korva.or.kr'
    ),
    2020: AppConfig(
        appid=2020,
        appname='2020_in_claws',
        appclass=parser.USA_tobyhannaParser,
        appdomain='www.tobyhanna.army.mil'
    ),
    4069: AppConfig(
        appid=4069,
        appname='4069_eg_dostor',
        appclass=parser.EG_dostorParser,
        appdomain='www.dostor.org'
    ),
    4070: AppConfig(
        appid=4070,
        appname='4070_af_tolonews',
        appclass=parser.AF_tolonewsParser,
        appdomain='www.tolonews.com'
    ),
    4000: AppConfig(
        appid=4000,
        appname='4000_ir_iranwatch',
        appclass=parser.IR_iranwatchParser,
        appdomain='www.iranwatch.org'
    ),
    4001: AppConfig(
        appid=4001,
        appname='4001_tw_vohcoom',
        appclass=parser.TW_vohcoomParser,
        appdomain='www.voh.com.tw'
    ),
    4002: AppConfig(
        appid=4002,
        appname='4002_tw_aaroc',
        appclass=parser.TW_aarocParser,
        appdomain='aaroc.edu.tw'
    ),
    4003: AppConfig(
        appid=4003,
        appname='4003_ly_jctrans',
        appclass=parser.LY_jctransParser,
        appdomain='lyd.org'
    ),
    4004: AppConfig(
        appid=4004,
        appname='4004_tw_inprorg',
        appclass=parser.TW_inprorgParser,
        appdomain='www.inpr.org.tw'
    ),
    4005: AppConfig(
        appid=4005,
        appname='4005_tw_wenxuecity',
        appclass=parser.TW_wenxuecityParser,
        appdomain='www.wenxuecity.com'
    ),
    4006: AppConfig(
        appid=4006,
        appname='4006_tw_businesstoday',
        appclass=parser.TW_businesstodayParser,
        appdomain='www.businesstoday.com.tw'
    ),
    4007: AppConfig(
        appid=4007,
        appname='4007_tw_greatnews',
        appclass=parser.TW_greatnewsParser,
        appdomain='www.greatnews.com.tw'
    ),
    4008: AppConfig(
        appid=4008,
        appname='4008_tw_hxnews',
        appclass=parser.TW_hxnewsParser,
        appdomain='www.hxnews.com'
    ),
    4009: AppConfig(
        appid=4009,
        appname='4009_jp_sakura',
        appclass=parser.JP_sakuraParser,
        appdomain='j-navy.sakura.ne.jp'
    ),
    4010: AppConfig(
        appid=4010,
        appname='4010_kr_dapa',
        appclass=parser.KR_dapaParser,
        appdomain='www.dapa.go.kr'
    ),
    4011: AppConfig(
        appid=4011,
        appname='4011_fr_rmaac',
        appclass=parser.FR_rmaacParser,
        appdomain='www.rma.ac.be'
    ),
    4012: AppConfig(
        appid=4012,
        appname='4012_ru_flot',
        appclass=parser.RU_flotParser,
        appdomain='flot.com'
    ),
    4013: AppConfig(
        appid=4013,
        appname='4013_ru_kommersant',
        appclass=parser.RU_kommersantParser,
        appdomain='russianforces.org'
    ),
    4014: AppConfig(
        appid=4014,
        appname='4014_vn_mofa',
        appclass=parser.VN_mofaParser,
        appdomain='www.mofa.gov.vn'
    ),
    4015: AppConfig(
        appid=4015,
        appname='4015_ir_online',
        appclass=parser.IR_onlineParser,
        appdomain='isis-online.org'
    ),
    4016: AppConfig(
        appid=4016,
        appname='4016_usa_specialoperations',
        appclass=parser.USA_specialoperationsParser,
        appdomain='specialoperations.com'
    ),
    4017: AppConfig(
        appid=4017,
        appname='4017_usa_rfaorg',
        appclass=parser.USA_rfaorgParser,
        appdomain='www.rfa.org'
    ),
    4018: AppConfig(
        appid=4018,
        appname='4018_usa_rfaorgkorean',
        appclass=parser.USA_rfaorgkoreanParser,
        appdomain='www.rfa.org/korean'
    ),
    4019: AppConfig(
        appid=4019,
        appname='4019_usa_rfaorgcantonese',
        appclass=parser.USA_rfaorgcantoneseParser,
        appdomain='www.rfa.org/cantonese'
    ),
    4020: AppConfig(
        appid=4020,
        appname='4020_usa_rfaorgenglish',
        appclass=parser.USA_rfaorgenglishParser,
        appdomain='www.rfa.org/english'
    ),
    4021: AppConfig(
        appid=4021,
        appname='4021_usa_rfaorgvietnamese',
        appclass=parser.USA_rfaorgvietnameseParser,
        appdomain='www.rfa.org/vietnamese'
    ),
    4022: AppConfig(
        appid=4022,
        appname='4022_usa_rfaorgburmese',
        appclass=parser.USA_rfaorgburmeseParser,
        appdomain='www.rfa.org/burmese'
    ),
    4023: AppConfig(
        appid=4023,
        appname='4023_usa_rfaorglao',
        appclass=parser.USA_rfaorglaoParser,
        appdomain='www.rfa.org/lao'
    ),
    4024: AppConfig(
        appid=4024,
        appname='4024_usa_rfaorgkhmer',
        appclass=parser.USA_rfaorgkhmerParser,
        appdomain='www.rfa.org/khmer'
    ),
    4025: AppConfig(
        appid=4025,
        appname='4025_usa_rfaorgtibetan',
        appclass=parser.USA_rfaorgtibetanParser,
        appdomain='www.rfa.org/tibetan'
    ),
    4026: AppConfig(
        appid=4026,
        appname='4026_tr_uyghurcongress',
        appclass=parser.TR_uyghurcongressParser,
        appdomain='www.uyghurcongress.org'
    ),
    4027: AppConfig(
        appid=4027,
        appname='4027_kr_kaoms',
        appclass=parser.KR_kaomsParser,
        appdomain='www.kaoms.or.kr'
    ),
    4028: AppConfig(
        appid=4028,
        appname='4028_ru_scramble',
        appclass=parser.RU_scrambleParser,
        appdomain='scramble.nl'
    ),
    4029: AppConfig(
        appid=4029,
        appname='4029_de_bundeswehr',
        appclass=parser.DE_bundeswehrParser,
        appdomain='www.bundeswehr.de'
    ),
    4030: AppConfig(
        appid=4030,
        appname='4030_pk_paknavy',
        appclass=parser.PK_paknavyParser,
        appdomain='www.paknavy.gov.pk'
    ),
    4031: AppConfig(
        appid=4031,
        appname='4031_in_indianairforce',
        appclass=parser.IN_indianairforceParser,
        appdomain='indianairforce.nic.in'
    ),
    4032: AppConfig(
        appid=4032,
        appname='4032_usa_nato',
        appclass=parser.USA_natoParser,
        appdomain='www.nato.int'
    ),
    4033: AppConfig(
        appid=4033,
        appname='4033_usa_enemyforces',
        appclass=parser.USA_enemyforcesParser,
        appdomain='www.enemyforces.net'
    ),
    4034: AppConfig(
        appid=4034,
        appname='4034_ru_russianforces',
        appclass=parser.RU_russianforcesParser,
        appdomain='russianforces.org'
    ),
    4035: AppConfig(
        appid=4035,
        appname='4035_tw_stormmg',
        appclass=parser.TW_stormmgParser,
        appdomain='new7.storm.mg'
    ),
    4036: AppConfig(
        appid=4036,
        appname='4036_usa_rfaorguyghur',
        appclass=parser.USA_rfaorguyghurParser,
        appdomain='www.rfa.org'
    ),
    4037: AppConfig(
        appid=4037,
        appname='4037_kp_globalsecurity',
        appclass=parser.KP_globalsecurityParser,
        appdomain='www.globalsecurity.org'
    ),
    # bw4
    4038: AppConfig(
        appid=4038,
        appname='4038_tw_judicial',
        appclass=parser.TW_judicialParser,
        appdomain='tps.judicial.gov.tw'
    ),
    4039: AppConfig(
        appid=4039,
        appname='4039_tw_tphjudicial',
        appclass=parser.TW_tphjudicialParser,
        appdomain='tph.judicial.gov.tw'
    ),
    4040: AppConfig(
        appid=4040,
        appname='4040_tw_rootlaw',
        appclass=parser.TW_rootlawParser,
        appdomain='www.rootlaw.com.tw'
    ),
    4041: AppConfig(
        appid=4041,
        appname='4041_tw_twincn',
        appclass=parser.TW_twincnParser,
        appdomain='dailyview.tw'
    ),
    4042: AppConfig(
        appid=4042,
        appname='4042_tw_tfctaiwan',
        appclass=parser.TW_tfctaiwanParser,
        appdomain='tfc-taiwan.org.tw'
    ),
    4043: AppConfig(
        appid=4043,
        appname='4043_usa_globaltaiwan',
        appclass=parser.USA_globaltaiwanParser,
        appdomain='globaltaiwan.org'
    ),
    4044: AppConfig(
        appid=4044,
        appname='4044_vn_thanhnien',
        appclass=parser.VN_thanhnienParser,
        appdomain='thanhnien.vn'
    ),
    4045: AppConfig(
        appid=4045,
        appname='4045_kh_cctimes',
        appclass=parser.KH_cctimesParser,
        appdomain='cc-times.com'
    ),
    4046: AppConfig(
        appid=4046,
        appname='4046_mm_modgovmn',
        appclass=parser.MM_modgovmnParser,
        appdomain='www.mod.gov.mn'
    ),
    4047: AppConfig(
        appid=4047,
        appname='4047_mm_irrawaddy',
        appclass=parser.MM_irrawaddyParser,
        appdomain='www.irrawaddy.com'
    ),
    4048: AppConfig(
        appid=4048,
        appname='4048_kr_bemilchosun',
        appclass=parser.KR_bemilchosunParser,
        appdomain='bemil.chosun.com'
    ),
    4049: AppConfig(
        appid=4049,
        appname='4049_mm_bbccom',
        appclass=parser.MM_bbccomParser,
        appdomain='www.bbc.com'
    ),
    4050: AppConfig(
        appid=4050,
        appname='4050_mm_voanews',
        appclass=parser.MM_voanewsParser,
        appdomain='burmese.voanews.com'
    ),
    4051: AppConfig(
        appid=4051,
        appname='4051_th_sanook',
        appclass=parser.TH_sanookParser,
        appdomain='www.sanook.com'
    ),
    4052: AppConfig(
        appid=4052,
        appname='4052_th_thairath',
        appclass=parser.TH_thairathParser,
        appdomain='www.thairath.co.th'
    ),
    4053: AppConfig(
        appid=4053,
        appname='4053_th_khaosod',
        appclass=parser.TH_khaosodParser,
        appdomain='www.khaosod.co.th'
    ),
    4054: AppConfig(
        appid=4054,
        appname='4054_th_mgronline',
        appclass=parser.TH_mgronlineParser,
        appdomain='www.mgronline.com'
    ),
    4055: AppConfig(
        appid=4055,
        appname='4055_th_isranews',
        appclass=parser.TH_isranewsParser,
        appdomain='www.isranews.org'
    ),
    4056: AppConfig(
        appid=4056,
        appname='4056_th_thaipost',
        appclass=parser.TH_thaipostParser,
        appdomain='www.thaipost.net'
    ),
    4057: AppConfig(
        appid=4057,
        appname='4057_th_matichon',
        appclass=parser.TH_matichonParser,
        appdomain='www.matichon.co.th'
    ),
    4058: AppConfig(
        appid=4058,
        appname='4058_th_naewna',
        appclass=parser.TH_naewnaParser,
        appdomain='www.naewna.com'
    ),
    4059: AppConfig(
        appid=4059,
        appname='4059_th_komchadluek',
        appclass=parser.TH_komchadluekParser,
        appdomain='www.komchadluek.net'
    ),
    4060: AppConfig(
        appid=4060,
        appname='4060_th_siamrath',
        appclass=parser.TH_siamrathParser,
        appdomain='www. siamrath.co.th'
    ),
    4061: AppConfig(
        appid=4061,
        appname='4061_th_banmuang',
        appclass=parser.TH_banmuangParser,
        appdomain='www.banmuang.co.th'
    ),
    4062: AppConfig(
        appid=4062,
        appname='4062_id_antaranews',
        appclass=parser.IdAntArAnewsParser,
        appdomain='www.antaranews.com'
    ),
    4063: AppConfig(
        appid=4063,
        appname='4063_id_jakartaglobe',
        appclass=parser.ID_jakartaglobeParser,
        appdomain='jakartaglobe.id'
    ),
    4064: AppConfig(
        appid=4064,
        appname='4064_th_nationnmultimedia',
        appclass=parser.TH_nationnmultimediaParser,
        appdomain='www.nationnmultimedia.com'
    ),
    4065: AppConfig(
        appid=4065,
        appname='4065_id_republika',
        appclass=parser.ID_republikaParser,
        appdomain='republika.co.id'
    ),
    4066: AppConfig(
        appid=4066,
        appname='4066_id_newsdetik',
        appclass=parser.ID_newsdetikParser,
        appdomain='news.detik.com'
    ),
    4067: AppConfig(
        appid=4067,
        appname='4067_my_malaysiasun',
        appclass=parser.MY_malaysiasunParser,
        appdomain='www.malaysiasun.com'
    ),
    4068: AppConfig(
        appid=4068,
        appname='4068_usa_energyvoice',
        appclass=parser.USA_energyvoiceParser,
        appdomain='www.energyvoice.com'
    ),
    4071: AppConfig(
        appid=4071,
        appname='4071_pk_thenews',
        appclass=parser.PK_thenewsParser,
        appdomain='www.thenews.com.pk'
    ),
    4072: AppConfig(
        appid=4072,
        appname='4072_pk_dailytimes',
        appclass=parser.PK_dailytimesParser,
        appdomain='www.dailytimes.com.pk'
    ),
    4073: AppConfig(
        appid=4073,
        appname='4073_pk_pakistan',
        appclass=parser.PK_pakistanParser,
        appdomain='www.pakistan.gov.pk'
    ),
    5000: AppConfig(
        appid=5000,
        appname='5000_cn_xuexi',
        appclass=parser.CN_xuexiParser,
        appdomain='www.xuexi.cn'
    ),
    5001: AppConfig(
        appid=5001,
        appname='5001_tw_yahoo',
        appclass=parser.TW_yahooParser,
        appdomain='tw.news.yahoo.com'
    ),
    5002: AppConfig(
        appid=5002,
        appname='5002_cn_cpcpeople',
        appclass=parser.CN_cpcpeopleParser,
        appdomain='cpc.people.com.cn'
    ),
    4077: AppConfig(
        appid=4077,
        appname='4077_tw_ksnews',
        appclass=parser.TW_ksnewsParser,
        appdomain='www.ksnews.com.tw'
    ),
    4078: AppConfig(
        appid=4078,
        appname='4078_tw_people',
        appclass=parser.TW_peopleParser,
        appdomain='tw.people.com.cn'
    ),
    4079: AppConfig(
        appid=4079,
        appname='4079_tw_pchome',
        appclass=parser.TW_pchomeParser,
        appdomain='news.pchome.com.tw'
    ),
    4081: AppConfig(
        appid=4081,
        appname='4081_pk_pafgov',
        appclass=parser.PK_pafgovParser,
        appdomain='paf.gov.pk'
    ),
    4082: AppConfig(
        appid=4082,
        appname='4082_ir_irannewsdaily',
        appclass=parser.IR_irannewsdailyParser,
        appdomain='irannewsdaily.com'
    ),
    4089: AppConfig(
        appid=4089,
        appname='4089_gb_instituteforgovernment',
        appclass=parser.GbInstituteForGovernmentParser,
        appdomain='www.instituteforgovernment.org.uk'
    ),
    4090: AppConfig(
        appid=4090,
        appname='4090_hk_vjmedia',
        appclass=parser.HkVjMediaParser,
        appdomain='www.vjmedia.com.hk'
    ),
    4091: AppConfig(
        appid=4091,
        appname='4091_hk_passiontimes',
        appclass=parser.HkPassionTimesParser,
        appdomain='www.passiontimes.hk'
    ),
    4092: AppConfig(
        appid=4092,
        appname='4092_hk_singpao',
        appclass=parser.HkSingPaoParser,
        appdomain='www.singpao.com.hk'
    ),
    4093: AppConfig(
        appid=4093,
        appname='4093_usa_carnegieeurope',
        appclass=parser.UsaCaneGieEuRopeParser,
        appdomain='carnegieeurope.eu'
    ),
    4094: AppConfig(
        appid=4094,
        appname='4094_usa_fivethirtyeight',
        appclass=parser.UsaFiveThirtyEightParser,
        appdomain='fivethirtyeight.com'
    ),
    4095: AppConfig(
        appid=4095,
        appname='4095_in_pib',
        appclass=parser.InPibParser,
        appdomain='pib.gov.in'
    ),
    4083: AppConfig(
        appid=4083,
        appname='4083_jp_rips',
        appclass=parser.JP_ripsParser,
        appdomain='www.rips.or.jp'
    ),
    4084: AppConfig(
        appid=4084,
        appname='4084_ca_asiapacific',
        appclass=parser.CA_asiapacificParser,
        appdomain='www.asiapacific.ca'
    ),
    4085: AppConfig(
        appid=4085,
        appname='4085_jp_npi',
        appclass=parser.JP_npiParser,
        appdomain='www.npi.or.jp'
    ),
    4086: AppConfig(
        appid=4086,
        appname='4086_kr_dema',
        appclass=parser.KR_demaParser,
        appdomain='kookbang.dema.mil.kr'
    ),
    4087: AppConfig(
        appid=4087,
        appname='4087_kr_naver',
        appclass=parser.KR_naverParser,
        appdomain='news.naver.com'
    ),
    4088: AppConfig(
        appid=4088,
        appname='4088_id_guojiribao',
        appclass=parser.ID_guojiribaoParser,
        appdomain='guojiribao.com'
    ),
    4097: AppConfig(
        appid=4097,
        appname='4097_in_gatewayhouse',
        appclass=parser.InGatewayHouseParser,
        appdomain='www.gatewayhouse.in'
    ),
    4098: AppConfig(
        appid=4098,
        appname='4098_se_sipri',
        appclass=parser.SeSipriParser,
        appdomain='www.sipri.org'
    ),
    4096: AppConfig(
        appid=4096,
        appname='4096_in_habibiecenter',
        appclass=parser.InHaBiBieCenterParser,
        appdomain='www.habibiecenter.or.id'

    ),
    4099: AppConfig(
        appid=4099,
        appname='4099_xz_tibetnetwork',
        appclass=parser.XzTibetNetWorkParser,
        appdomain='tibetnetwork.org'
    ),
    4100: AppConfig(
        appid=4100,
        appname='4100_xz_phayul',
        appclass=parser.XzPhaYulParser,
        appdomain='www.phayul.com'
    ),
    4101: AppConfig(
        appid=4101,
        appname='4101_nl_clingendael',
        appclass=parser.NlClinGenDaelParser,
        appdomain='www.clingendael.org'
    ),
    4102: AppConfig(
        appid=4102,
        appname='4102_in_indianarmy',
        appclass=parser.InIndianArmyParser,
        appdomain='indianarmy.nic.in'
    ),
    4103: AppConfig(
        appid=4103,
        appname='4103_xz_zhiye',
        appclass=parser.XzZhiYeParser,
        appdomain='xizang-zhiye.org'
    ),
    4104: AppConfig(
        appid=4104,
        appname='4104_tw_kannewyork',
        appclass=parser.TwKanNewYorkParser,
        appdomain='www.kannewyork.com'
    ),
    4105: AppConfig(
        appid=4105,
        appname='4105_hk_pathofdemocracy',
        appclass=parser.HkPathOfDemocracyParser,
        appdomain='pathofdemocracy.hk'
    ),
    4106: AppConfig(
        appid=4106,
        appname='4106_usa_hrf',
        appclass=parser.UsaHrfParser,
        appdomain='hrf.org'
    ),
    4107: AppConfig(
        appid=4107,
        appname='4107_hk_civicparty',
        appclass=parser.HkCivicPartyParser,
        appdomain='www.civicparty.hk'
    ),
    4108: AppConfig(
        appid=4108,
        appname='4108_my_mier',
        appclass=parser.MyMiErParser,
        appdomain='www.mier.org.my'
    ),
    4109: AppConfig(
        appid=4109,
        appname='4109_vn_dav',
        appclass=parser.VnDavParser,
        appdomain='www.dav.edu.vn'
    ),
    4110: AppConfig(
        appid=4110,
        appname='4110_in_maritimeindia',
        appclass=parser.InMariTimeIndiaParser,
        appdomain='maritimeindia.org'
    ),
    4111: AppConfig(
        appid=4111,
        appname='4111_ru_4pt',
        appclass=parser.Ru4ptParser,
        appdomain='www.4pt.su'
    ),
    4112: AppConfig(
        appid=4112,
        appname='4112_usa_misawa',
        appclass=parser.UsaMiSawaParser,
        appdomain='www.misawa.af.mil'
    ),
    4113: AppConfig(
        appid=4113,
        appname='4113_usa_kadena',
        appclass=parser.UsaKaDenaParser,
        appdomain='www.kadena.af.mil'
    ),
    4114: AppConfig(
        appid=4114,
        appname='4114_usa_andersen',
        appclass=parser.UsaAnDerDenParser,
        appdomain='www.andersen.af.mil'
    ),
    4115: AppConfig(
        appid=4115,
        appname='4115_usa_yokota',
        appclass=parser.UsaYoKoTaParser,
        appdomain='www.yokota.af.mil'
    ),
    4116: AppConfig(
        appid=4116,
        appname='4116_usa_dni',
        appclass=parser.UsaDniParser,
        appdomain='www.dni.gov'
    ),
    4117: AppConfig(
        appid=4117,
        appname='4117_usa_af',
        appclass=parser.UsaAfParser,
        appdomain='www.af.mil'
    ),
    4118: AppConfig(
        appid=4118,
        appname='4118_usa_fap',
        appclass=parser.UsaFpaParser,
        appdomain='www.fpa.org'
    ),
    4119: AppConfig(
        appid=4119,
        appname='4119_usa_mitre',
        appclass=parser.UsaMitreParser,
        appdomain='www.mitre.org'
    ),
    4120: AppConfig(
        appid=4120,
        appname='4120_usa_potomacinstitute',
        appclass=parser.UsaPotomacInstituteParser,
        appdomain='www.mitre.org'
    ),
    4121: AppConfig(
        appid=4121,
        appname='4121_usa_afrl',
        appclass=parser.UsaAfRlParser,
        appdomain='www.afrl.af.mil'
    ),
    4122: AppConfig(
        appid=4122,
        appname='4122_hk_aastocks',
        appclass=parser.HkAasTocKsParser,
        appdomain='www.aastocks.com'
    ),
    4123: AppConfig(
        appid=4123,
        appname='4123_usa_tngov',
        appclass=parser.UsaTnGovParser,
        appdomain='www.tn.gov'
    ),
    4124: AppConfig(
        appid=4124,
        appname='4124_usa_transportation',
        appclass=parser.UsaTranSporTaTionParser,
        appdomain='www.transportation.gov'
    ),
    4125: AppConfig(
        appid=4125,
        appname='4125_tw_eventsinfocus',
        appclass=parser.TwEventSinFocusParser,
        appdomain='www.eventsinfocus.org'
    ),
    4126: AppConfig(
        appid=4126,
        appname='4126_tz_stipro',
        appclass=parser.TzStiProParser,
        appdomain='www.stipro.or.tz'
    ),
    4127: AppConfig(
        appid=4127,
        appname='4127_usa_usac',
        appclass=parser.UsaUsAcParser,
        appdomain='iies.usac.edu.gt'
    ),
    4128: AppConfig(
        appid=4128,
        appname='4128_gt_cees',
        appclass=parser.GtCeesParser,
        appdomain='www.cees.org.gt'
    ),
    4129: AppConfig(
        appid=4129,
        appname='4129_bo_fundacion',
        appclass=parser.BoFundaCionParser,
        appdomain='fundacion-milenio.org'
    ),
    4130: AppConfig(
        appid=4130,
        appname='4130_bo_aru',
        appclass=parser.BoAruParser,
        appdomain='www.aru.org.bo'
    ),
    4131: AppConfig(
        appid=4131,
        appname='4131_bo_cipca',
        appclass=parser.BoCipCaParser,
        appdomain='cipca.org.bo'
    ),
    4132: AppConfig(
        appid=4132,
        appname='4132_vn_vnexpress',
        appclass=parser.VnvNexPressParser,
        appdomain='vnexpress.net'
    ),
    4133: AppConfig(
        appid=4133,
        appname='4133_za_irr',
        appclass=parser.ZaIrrParser,
        appdomain='irr.org.za'
    ),
    4134: AppConfig(
        appid=4134,
        appname='4134_za_dpru',
        appclass=parser.ZaDpRuParser,
        appdomain='www.dpru.uct.ac.za'
    ),
    4135: AppConfig(
        appid=4135,
        appname='4135_usa_afmil',
        appclass=parser.UsaAfMilParser,
        appdomain='www.af.mil'
    ),
    4136: AppConfig(
        appid=4136,
        appname='4136_usa_uspto',
        appclass=parser.UsaUsPtoParser,
        appdomain='www.uspto.gov'
    ),
    4137: AppConfig(
        appid=4137,
        appname='4137_usa_mbta',
        appclass=parser.UsaMbtaParser,
        appdomain='www.mbta.com'
    ),
    # 4138: AppConfig(
    #     appid=4138,
    #     appname='4138_usa_dnigov',
    #     appclass=parser.UsaDinGovParser,
    #     appdomain='www.dni.gov'
    # ),
    4139: AppConfig(
        appid=4139,
        appname='4139_usa_piie',
        appclass=parser.UsaPiIeParser,
        appdomain='www.piie.com'
    ),
    4140: AppConfig(
        appid=4140,
        appname='4140_usa_nist',
        appclass=parser.UsaNistParser,
        appdomain='www.nist.gov'
    ),
    4141: AppConfig(
        appid=4141,
        appname='4141_usa_colorado',
        appclass=parser.UsaColoradoParser,
        appdomain='www.colorado.gov'
    ),
    4142: AppConfig(
        appid=4142,
        appname='4142_usa_fbi',
        appclass=parser.UsaFbiParser,
        appdomain='www.fbi.gov'
    ),
    4143: AppConfig(
        appid=4143,
        appname='4143_usa_rockefellerfoundation',
        appclass=parser.UsaRockefellerFoundationParser,
        appdomain='www.rockefellerfoundation.org'
    ),
    4144: AppConfig(
        appid=4144,
        appname='4144_usa_cms',
        appclass=parser.UsaCmsParser,
        appdomain='www.cms.gov'
    ),
    4145: AppConfig(
        appid=4145,
        appname='4145_usa_gaports',
        appclass=parser.UsaGaPortsParser,
        appdomain='gaports.com'
    ),
    4146: AppConfig(
        appid=4146,
        appname='4146_usa_edgov',
        appclass=parser.UsaEdGovParser,
        appdomain='www.ed.gov'
    ),
    4147: AppConfig(
        appid=4147,
        appname='4147_usa_carnegieendowment',
        appclass=parser.UsaCarneGieEnDowMentParser,
        appdomain='carnegieendowment.org'
    ),
    4148: AppConfig(
        appid=4148,
        appname='4148_usa_princeton',
        appclass=parser.UsaPrincetonParser,
        appdomain='www.princeton.edu'
    ),
    4149: AppConfig(
        appid=4149,
        appname='4149_usa_noaa',
        appclass=parser.UsaNoaaParser,
        appdomain='www.noaa.gov'
    ),
    4150: AppConfig(
        appid=4150,
        appname='4150_usa_energy',
        appclass=parser.UsaEnergyParser,
        appdomain='www.energy.gov'
    ),
    4151: AppConfig(
        appid=4151,
        appname='4151_usa_ncgov',
        appclass=parser.UsaNcGovParser,
        appdomain='www.nc.gov'
    ),
    4152: AppConfig(
        appid=4152,
        appname='4152_usa_cpsc',
        appclass=parser.UsaCpScParser,
        appdomain='www.cpsc.gov'
    ),
    4153: AppConfig(
        appid=4153,
        appname='4153_ug_misr',
        appclass=parser.UgMiSrParser,
        appdomain='misr.mak.ac.ug'
    ),
    4154: AppConfig(
        appid=4154,
        appname='4154_ng_niia',
        appclass=parser.NgNiIaParser,
        appdomain='niia.gov.ng'
    ),
    4155: AppConfig(
        appid=4155,
        appname='4155_usa_cps',
        appclass=parser.UsaCpsParser,
        appdomain='cps.ceu.edu'
    ),
    4156: AppConfig(
        appid=4156,
        appname='4156_usa_ecfr',
        appclass=parser.UsaEcFrParser,
        appdomain='ecfr.eu'
    ),
    4157: AppConfig(
        appid=4157,
        appname='4157_usa_research',
        appclass=parser.UsaResearchParser,
        appdomain='www.case-research.eu'
    ),
    4158: AppConfig(
        appid=4158,
        appname='4158_usa_prio',
        appclass=parser.UsaPrioParser,
        appdomain='www.prio.org'
    ),

    5003: AppConfig(
        appid=5003,
        appname='5003_usa_hollywoodreporter',
        appclass=parser.UsaHollywoodreporterParser,
        appdomain='www.hollywoodreporter.com'
    ),
    5004: AppConfig(
        appid=5004,
        appname='5004_uk_fpc',
        appclass=parser.UkFpcParser,
        appdomain='fpc.org.uk'
    ),
    5005: AppConfig(
        appid=5005,
        appname='5005_uk_policynetwork',
        appclass=parser.UkPolicynetworkParser,
        appdomain='policynetwork.org'
    ),
    5006: AppConfig(
        appid=5006,
        appname='5006_in_li',
        appclass=parser.InLiParser,
        appdomain='li.com'
    ),
    5007: AppConfig(
        appid=5007,
        appname='5007_uk_fabians',
        appclass=parser.UkFabiansParser,
        appdomain='fabians.org.uk'
    ),
    4166: AppConfig(
        appid=4166,
        appname='4166_pa_senacyt',
        appclass=parser.PaSenaCytParser,
        appdomain='www.senacyt.gob.pa'
    ),
    4167: AppConfig(
        appid=4167,
        appname='4167_uscg',
        appclass=parser.UsaUscgParser,
        appdomain='www.news.uscg.mil'
    ),
    4168: AppConfig(
        appid=4168,
        appname='4168_clevelandfg',
        appclass=parser.UsaClevelandfgParser,
        appdomain='www.clevelandfg.com'
    ),
    4169: AppConfig(
        appid=4169,
        appname='4169_fase',
        appclass=parser.BrFaseParser,
        appdomain='www.fase.org.br'
    ),
    4170: AppConfig(
        appid=4170,
        appname='4170_taichung',
        appclass=parser.TwTaichungParser,
        appdomain='www.taichung.gov.tw'
    ),
    4171: AppConfig(
        appid=4171,
        appname='4171_newsmarket',
        appclass=parser.TwNewsmarketParser,
        appdomain='www.newsmarket.com.tw'
    ),
    4159: AppConfig(
        appid=4159,
        appname='4159_pr_grupocne',
        appclass=parser.PrGruPoCneParser,
        appdomain='grupocne.org'
    ),
    4160: AppConfig(
        appid=4160,
        appname='4160_eg_cedej',
        appclass=parser.EgCedEjParser,
        appdomain='cedej-eg.org'
    ),
    4161: AppConfig(
        appid=4161,
        appname='4161_uk_ifs',
        appclass=parser.UkIfsParser,
        appdomain='ifs.org.uk'
    ),
    4162: AppConfig(
        appid=4162,
        appname='4162_uk_wikileaks',
        appclass=parser.UkWikiLeaksParser,
        appdomain='wikileaks.org'
    ),
    4163: AppConfig(
        appid=4163,
        appname='4163_hn_fosdeh',
        appclass=parser.HnFosDehParser,
        appdomain='fosdeh.com'
    ),
    4164: AppConfig(
        appid=4164,
        appname='4164_usa_ftc',
        appclass=parser.UsaFtcParser,
        appdomain='www.ftc.gov'
    ),
    4165: AppConfig(
        appid=4165,
        appname='4165_usa_hhs',
        appclass=parser.UsaHhsParser,
        appdomain='www.hhs.gov'
    ),
    5008:AppConfig(
        appid=5008,
        appname='5008_uk_centreforprogressivecapitalism',
        appclass=parser.UkCentreforprogressiveCapitalismParser,
        appdomain='centreforprogressivecapitalism-archive.net'
    ),
    5009:AppConfig(
        appid=5009,
        appname='5009_uk_crppoliscamac',
        appclass=parser.UkCrppolisCamaCParser,
        appdomain='www.crp.polis.cam.ac.uk'
    ),
    5010: AppConfig(
        appid=5010,
        appname='5010_uk_niesr',
        appclass=parser.UkNiesrParser,
        appdomain='www.niesr.ac.uk'
    ),
    5011:AppConfig(
        appid=5011,
        appname='5011_uk_sussex',
        appclass=parser.UkSuSSexParser,
        appdomain='www.sussex.ac.uk'
    ),
    5012:AppConfig(
        appid=5012,
        appname='5012_usa_asiasociety',
        appclass=parser.UsaAsiAsocietyParser,
        appdomain='asiasociety.org'
    ),
    5013:AppConfig(
        appid=5013,
        appname='5013_usa_fas',
        appclass=parser.UsaFasParser,
        appdomain='fas.org'
    ),
    5014:AppConfig(
        appid=5014,
        appname='5014_cn_savetibet',
        appclass=parser.CnSavetibetParser,
        appdomain='savetibet.org'
    ),
    5015:AppConfig(
        appid=5015,
        appname='5015_hk_eoc',
        appclass=parser.HkEocParser,
        appdomain='www.eoc.org.hk'
    ),
    5016:AppConfig(
        appid=5016,
        appname='5016_hk_msf',
        appclass=parser.HkMsfParser,
        appdomain='msf.hk'
    ),
    5017:AppConfig(
        appid=5017,
        appname='5017_cn_dalailama',
        appclass=parser.CnDalailamaParser,
        appdomain='www.dalailama.com'
    ),
    4172: AppConfig(
        appid=4172,
        appname='4172_munkschool',
        appclass=parser.CaMunkschoolParser,
        appdomain='munkschool.utoronto.ca'
    ),
    4173: AppConfig(
        appid=4173,
        appname='4173_canada2020',
        appclass=parser.CaCanada2020Parser,
        appdomain='canada2020.ca'
    ),
    4174: AppConfig(
        appid=4174,
        appname='4174_bidpa',
        appclass=parser.CaBidpaParser,
        appdomain='bidpa.bw'
    ),
    4175: AppConfig(
        appid=4175,
        appname='4175_irpp',
        appclass=parser.InIrppParser,
        appdomain='irpp.org'
    ),
    4176: AppConfig(
        appid=4176,
        appname='4176_orfonline',
        appclass=parser.InOrfOnlineParser,
        appdomain='www.orfonline.org'
    ),
    4177: AppConfig(
        appid=4177,
        appname='4177_governanceinnovation',
        appclass=parser.InGovernanceinnovationParser,
        appdomain='governanceinnovation.org'
    ),
    4178: AppConfig(
        appid=4178,
        appname='4178_africafoicentre',
        appclass=parser.InAfricAfoicentreParser,
        appdomain='africafoicentre.org'
    ),
    4179: AppConfig(
        appid=4179,
        appname='4179_usiofindia',
        appclass=parser.InUsiofindiaParser,
        appdomain='usiofindia.org'
    ),
    5018:AppConfig(
        appid=5018,
        appname='5018_jp_mainichi',
        appclass=parser.JpMainichiParser,
        appdomain='mainichi.jp'
    ),
    5019:AppConfig(
        appid=5019,
        appname='5019_vn_ciem',
        appclass=parser.VnCiemParser,
        appdomain='ciem.org.vn'
    ),
    5020:AppConfig(
        appid=5020,
        appname='5020_ca_ciia',
        appclass=parser.CaCiiaParser,
        appdomain='www.ciia.org'
    ),
    5021:AppConfig(
        appid=5021,
        appname='5021_kr_kyungnam',
        appclass=parser.KrKyungnamParser,
        appdomain='ifes.kyungnam.ac.kr'
    ),
    5022:AppConfig(
        appid=5022,
        appname='5022_uk_respublica',
        appclass=parser.UkRespublicaParser,
        appdomain='www.respublica.org.uk'
    ),
    5023:AppConfig(
        appid=5023,
        appname='5023_in_devinit',
        appclass=parser.InDevinitParser,
        appdomain='devinit.org'
    ),
    5024:AppConfig(
        appid=5024,
        appname='5024_uk_forumforthefuture',
        appclass=parser.UkForumFortheFutureParser,
        appdomain='www.forumforthefuture.org'
    ),
    5025:AppConfig(
        appid=5025,
        appname='5025_jp_asahi',
        appclass=parser.JpAsAhiParser,
        appdomain='www.asahi.com'
    ),
    5026:AppConfig(
        appid=5026,
        appname='5026_in_insightsonindia',
        appclass=parser.InInsIghtsonIndIaParser,
        appdomain='www.insightsonindia.com'
    ),
    5027:AppConfig(
        appid=5027,
        appname='5027_hk_hkcnews',
        appclass=parser.HkHkcnewsParser,
        appdomain='www.hkcnews.com'
    ),
    5028:AppConfig(
        appid=5028,
        appname='5028_usa_westpoint',
        appclass=parser.UsaWestpointParser,
        appdomain='www.westpoint.edu'
    ),
    5029:AppConfig(
        appid=5029,
        appname='5029_tw_nantou',
        appclass=parser.TwNaNtouParser,
        appdomain='www.nantou.gov.tw'
    ),
    5030:AppConfig(
        appid=5030,
        appname='5030_usa_cbp',
        appclass=parser.UsaCbpParser,
        appdomain='www.cbp.gov'
    ),
    5031:AppConfig(
        appid=5031,
        appname='5031_usa_dea',
        appclass=parser.UsaDeaParser,
        appdomain='www.dea.gov'
    ),
    5032:AppConfig(
        appid=5032,
        appname='5032_usa_dodcio',
        appclass=parser.UsaDoDcioParser,
        appdomain='dodcio.defense.gov'
    ),
    5033:AppConfig(
        appid=5033,
        appname='5033_usa_fundacionfaes',
        appclass=parser.UsaFundacionFaesParser,
        appdomain='fundacionfaes.org'
    ),
    5034:AppConfig(
        appid=5034,
        appname='5034_usa_nassauinstitute',
        appclass=parser.UsaNassauiNstituteParser,
        appdomain='www.nassauinstitute.org'
    ),
    5035:AppConfig(
        appid=5035,
        appname='5035_usa_gsa',
        appclass=parser.UsaGsaParser,
        appdomain='www.gsa.gov'
    ),
    5036:AppConfig(
        appid=5036,
        appname='5036_usa_uyghurcongress',
        appclass=parser.UsaUyghUrcongressParser,
        appdomain='www.uyghurcongress.org'
    ),
    5037:AppConfig(
        appid=5037,
        appname='5037_usa_uscis',
        appclass=parser.UsaUscisParser,
        appdomain='www.uscis.gov'
    ),
    4180: AppConfig(
        appid=4180,
        appname='4180_maryland',
        appclass=parser.UsaMarylandParser,
        appdomain='news.maryland.gov'
    ),
    4181: AppConfig(
        appid=4181,
        appname='4181_stripes',
        appclass=parser.UsaStripeSParser,
        appdomain='www.stripes.com'
    ),
    4182: AppConfig(
        appid=4182,
        appname='4182_clacso',
        appclass=parser.UsaClaCsoParser,
        appdomain='www.clacso.org'
    ),
    4183: AppConfig(
        appid=4183,
        appname='4183_weather',
        appclass=parser.UsaWeatherParser,
        appdomain='www.weather.gov'
    ),
    4184: AppConfig(
        appid=4184,
        appname='4184_afsoc',
        appclass=parser.UsaAfsocParser,
        appdomain='www.afsoc.af.mil'
    ),
    4185: AppConfig(
        appid=4185,
        appname='4185_usgs',
        appclass=parser.UsaUsgsParser,
        appdomain='www.usgs.gov'
    ),
    4186: AppConfig(
        appid=4186,
        appname='4186_usda',
        appclass=parser.UsaUsdaParser,
        appdomain='www.usda.gov'
    ),
    4187: AppConfig(
        appid=4187,
        appname='4187_curi',
        appclass=parser.UyCuriParser,
        appdomain='curi.org.uy'
    ),
    4199: AppConfig(
        appid=4199,
        appname='4199_crisisgroup',
        appclass=parser.UsaCrisisgroupParser,
        appdomain='www.crisisgroup.org'
    ),
    4200: AppConfig(
        appid=4200,
        appname='4200_cide',
        appclass=parser.MxCideParser,
        appdomain='www.cide.edu'
    ),
    4201: AppConfig(
        appid=4201,
        appname='4201_iep',
        appclass=parser.PeIepParser,
        appdomain='iep.org.pe'
    ),
    4202: AppConfig(
        appid=4202,
        appname='4202_usace',
        appclass=parser.UsaUsaceParser,
        appdomain='www.mvn.usace.army.mil'
    ),
    4203: AppConfig(
        appid=4203,
        appname='4203_iric',
        appclass=parser.KhIrIcParser,
        appdomain='iric.gov.kh'
    ),
    4204: AppConfig(
        appid=4204,
        appname='4204_marubeni',
        appclass=parser.JpMarubeniParser,
        appdomain='www.marubeni.com'
    ),
    4205: AppConfig(
        appid=4205,
        appname='4205_cartercenter',
        appclass=parser.UsaCarterCenterParser,
        appdomain='www.cartercenter.org'
    ),
    4188: AppConfig(
        appid=4188,
        appname='4188_carnegieindia',
        appclass=parser.InCarnegieindiaParser,
        appdomain='carnegieindia.org'
    ),
    4189: AppConfig(
        appid=4189,
        appname='4189_freedomhouse',
        appclass=parser.UsaFreedomhouseParser,
        appdomain='freedomhouse.org'
    ),
    4190: AppConfig(
        appid=4190,
        appname='4190_lexingtoninstitute',
        appclass=parser.UsaLexingtoninstituteParser,
        appdomain='www.lexingtoninstitute.org'
    ),
    4191: AppConfig(
        appid=4191,
        appname='4191_tongilvoice',
        appclass=parser.KrTongilvoiceParser,
        appdomain='www.tongilvoice.com'
    ),
    4192: AppConfig(
        appid=4192,
        appname='4192_opensocietyfoundations',
        appclass=parser.UsaOpensOcietyfOundatiOnsParser,
        appdomain='www.opensocietyfoundations.org'
    ),
    4193: AppConfig(
        appid=4193,
        appname='4193_cable',
        appclass=parser.HkCableParser,
        appdomain='www.i-cable.com'
    ),
    4194: AppConfig(
        appid=4194,
        appname='4194_eastday',
        appclass=parser.CnEastdayParser,
        appdomain='english.eastday.com'
    ),
    6000: AppConfig(
        appid=6000,
        appname='6000_hk_hkpri',
        appclass=parser.Hk_hkpriParser,
        appdomain='www.hkpri.org.hk'
    ),
    6001: AppConfig(
        appid=6001,
        appname='6001_hk_hket',
        appclass=parser.Hk_hketParser,
        appdomain='china.hket.com'
    ),
    6002: AppConfig(
        appid=6002,
        appname='6002_hk_lsd',
        appclass=parser.Hk_lsdParser,
        appdomain='www.lsd.org.hk'
    ),
    6003: AppConfig(
        appid=6003,
        appname='6003_kp_38north',
        appclass=parser.Kp_38northParser,
        appdomain='www.38north.org'
    ),
    6004: AppConfig(
        appid=6004,
        appname='6004_jp_okazaki',
        appclass=parser.Jp_okazakiParser,
        appdomain='okazaki-institute.org'
    ),
    6005: AppConfig(
        appid=6005,
        appname='6005_kr_mofa',
        appclass=parser.Kr_mofaParser,
        appdomain='www.mofa.go.kr'
    ),
    4210: AppConfig(
        appid=4210,
        appname='4210_lipi',
        appclass=parser.IdLipiParser,
        appdomain='lipi.go.id'
    ),
    4211: AppConfig(
        appid=4211,
        appname='4211_ipcs',
        appclass=parser.InIpcsParser,
        appdomain='www.ipcs.org'
    ),
    4212: AppConfig(
        appid=4212,
        appname='4212_rsisedu',
        appclass=parser.SgRsiseduParser,
        appdomain='www.rsis.edu.sg'
    ),
    4213: AppConfig(
        appid=4213,
        appname='4213_mgimo',
        appclass=parser.RuMgiMoParser,
        appdomain='english.mgimo.ru'
    ),
    4214: AppConfig(
        appid=4214,
        appname='4214_kapsarc',
        appclass=parser.SaKapsarcParser,
        appdomain='www.kapsarc.org'
    ),
    4215: AppConfig(
        appid=4215,
        appname='4215_macaupostdaily',
        appclass=parser.MoMacaupostdailyParser,
        appdomain='www.macaupostdaily.com'
    ),
    4216: AppConfig(
        appid=4216,
        appname='4216_cmcc',
        appclass=parser.ItCmCCParser,
        appdomain='www.cmcc.it'
    ),
    4217: AppConfig(
        appid=4217,
        appname='4217_feem',
        appclass=parser.ItFeemParser,
        appdomain='www.feem.it'
    ),
    4195: AppConfig(
        appid=4195,
        appname='4195_apcss',
        appclass=parser.UsaApcssParser,
        appdomain='apcss.org'
    ),
    4196: AppConfig(
        appid=4196,
        appname='4196_marinecorpstimes',
        appclass=parser.UsaMarinecorpstiMesParser,
        appdomain='www.marinecorpstimes.com'
    ),
    4197: AppConfig(
        appid=4197,
        appname='4197_instituteofwater',
        appclass=parser.GbInstItuteofwaterParser,
        appdomain='www.instituteofwater.org.uk'
    ),
    4198: AppConfig(
        appid=4198,
        appname='4198_cranfield',
        appclass=parser.GbCranfieldParser,
        appdomain='www.cranfield.ac.uk'
    ),
    4206: AppConfig(
        appid=4206,
        appname='4206_bristol',
        appclass=parser.GbBristolParser,
        appdomain='www.bristol.ac.uk'
    ),
    4207: AppConfig(
        appid=4207,
        appname='4207_hkiac',
        appclass=parser.HkHkiacParser,
        appdomain='www.hkiac.org'
    ),
    4208: AppConfig(
        appid=4208,
        appname='4208_law',
        appclass=parser.HkLawParser,
        appdomain='www.law.hku.hk'
    ),
    4209: AppConfig(
        appid=4209,
        appname='4209_fusades',
        appclass=parser.SvFusadesParser,
        appdomain='fusades.org'
    ),

    5038:AppConfig(
        appid=5038,
        appname='5038_mx_mexicoevalua',
        appclass=parser.MxMexicoevaluaParser,
        appdomain='www.mexicoevalua.org'
    ),
    5039:AppConfig(
        appid=5039,
        appname='5039_ca_iedm',
        appclass=parser.CaIedmParser,
        appdomain='www.iedm.org'
    ),
    5040:AppConfig(
        appid=5040,
        appname='5040_ca_thecic',
        appclass=parser.CaThecicParser,
        appdomain='thecic.org'
    ),
    5041:AppConfig(
        appid=5041,
        appname='5041_ca_mackenzieinstitute',
        appclass=parser.CaMackenzieinstituteParser,
        appdomain='mackenzieinstitute.com'
    ),
    5042:AppConfig(
        appid=5042,
        appname='5042_ca_macdonaldlaurier',
        appclass=parser.CaMacdonaldlaurierParser,
        appdomain='www.macdonaldlaurier.ca'
    ),
    5043:AppConfig(
        appid=5043,
        appname='5043_id_indeks',
        appclass=parser.IdIndeksParser,
        appdomain='indeks.kompas.com'
    ),
    5044:AppConfig(
        appid=5044,
        appname='5044_tr_maarip',
        appclass=parser.TrMaaripParser,
        appdomain='maarip.org'
    ),
    5045:AppConfig(
        appid=5045,
        appname='5045_es_fermintoro',
        appclass=parser.EsFermintoroParser,
        appdomain='fermintoro.net'
    ),
    5046:AppConfig(
        appid=5046,
        appname='5046_es_ifuturo',
        appclass=parser.EsIfuturoParser,
        appdomain='ifuturo.org'
    ),
    5047:AppConfig(
        appid=5047,
        appname='5047_es_cieplan',
        appclass=parser.EsCieplanParser,
        appdomain='www.cieplan.org'
    ),
    5060:AppConfig(
        appid=5060,
        appname='5060_in_newsindianexpress',
        appclass=parser.InNewsiNdiaNexpressParser,
        appdomain='newsindianexpress.com'
    ),
    5061:AppConfig(
        appid=5061,
        appname='5061_in_indiandefensenews',
        appclass=parser.InIndIandefensenewsParser,
        appdomain='www.indiandefensenews.in'
    ),
    5062:AppConfig(
        appid=5062,
        appname='5062_in_ndtv',
        appclass=parser.InNdtvParser,
        appdomain='www.ndtv.com'
    ),
    5063:AppConfig(
        appid=5063,
        appname='5063_in_indiastrategic',
        appclass=parser.InIndIastrategIcParser,
        appdomain='www.indiastrategic.in'
    ),
    5064:AppConfig(
        appid=5064,
        appname='5064_in_bhaskar',
        appclass=parser.InBhaskarParser,
        appdomain='www.bhaskar.com'
    ),
    5065:AppConfig(
        appid=5065,
        appname='5065_usa_nsf',
        appclass=parser.UsaNsfParser,
        appdomain='www.nsf.gov'
    ),
    5066:AppConfig(
        appid=5066,
        appname='5066_usa_uyghurnet',
        appclass=parser.UsaUyghUrnetParser,
        appdomain='www.uyghurnet.org'
    ),
    5048:AppConfig(
        appid=5048,
        appname='5048_es_dejusticia',
        appclass=parser.EsDejusticiaParser,
        appdomain='www.dejusticia.org'
    ),
    5049:AppConfig(
        appid=5049,
        appname='5049_in_theprint',
        appclass=parser.InTheprinTParser,
        appdomain='theprint.in'
    ),
    5050:AppConfig(
        appid=5050,
        appname='5050_au_internationalaffairs',
        appclass=parser.AuInternatIonalaffaIrsParser,
        appdomain='www.internationalaffairs.org.au'
    ),
    5051:AppConfig(
        appid=5051,
        appname='5051_my_lankadeepa',
        appclass=parser.MyLankadeepaParser,
        appdomain='www.lankadeepa.lk'
    ),
    5052:AppConfig(
        appid=5052,
        appname='5052_za_saiia',
        appclass=parser.ZaSaiiaParser,
        appdomain='saiia.org.za'
    ),
    5053:AppConfig(
        appid=5053,
        appname='5053_kr_unikorea',
        appclass=parser.KrUnikoreaParser,
        appdomain='unikorea.go.kr'
    ),
    5054:AppConfig(
        appid=5054,
        appname='5054_bt_kuenselonline',
        appclass=parser.BtKuenselonlineParser,
        appdomain='kuenselonline.com'
    ),
    5055:AppConfig(
        appid=5055,
        appname='5055_in_sundayguardianlive',
        appclass=parser.InSundayguardianliveParser,
        appdomain='www.sundayguardianlive.com'
    ),
    5056:AppConfig(
        appid=5056,
        appname='5056_in_newsx',
        appclass=parser.InNewsxParser,
        appdomain='www.newsx.com'
    ),
    5057:AppConfig(
        appid=5057,
        appname='5057_in_hindustantimes',
        appclass=parser.InHindustantimesParser,
        appdomain='www.hindustantimes.com'
    ),
    5058:AppConfig(
        appid=5058,
        appname='5058_in_naidunia',
        appclass=parser.InNaiduNiaParser,
        appdomain='www.naidunia.com'
    ),
    5059:AppConfig(
        appid=5059,
        appname='5059_in_outlookindia',
        appclass=parser.InOutlOOkindiaParser,
        appdomain='www.outlookindia.com'
    ),
    4218: AppConfig(
        appid=4218,
        appname='4218_bids',
        appclass=parser.BdBidsParser,
        appdomain='bids.org.bd'
    ),
    4219: AppConfig(
        appid=4219,
        appname='4219_pensamientocolombia',
        appclass=parser.CoPensamientocolombiaParser,
        appdomain='pensamientocolombia.org'
    ),
    4220: AppConfig(
        appid=4220,
        appname='4220_cebri',
        appclass=parser.BrCebriParser,
        appdomain='www.cebri.org'
    ),
    4221: AppConfig(
        appid=4221,
        appname='4221_cuhk',
        appclass=parser.HkCuhkParser,
        appdomain='www.com.cuhk.edu.hk'
    ),
    4222: AppConfig(
        appid=4222,
        appname='4222_jhsjk',
        appclass=parser.CnJhsJkParser,
        appdomain='jhsjk.people.cn'
    ),
    4223: AppConfig(
        appid=4223,
        appname='4223_taiwanhot',
        appclass=parser.TwTaiwanhoTParser,
        appdomain='www.taiwanhot.net'
    ),
    4224: AppConfig(
        appid=4224,
        appname='4224_lygov',
        appclass=parser.TwLygovParser,
        appdomain='www.ly.gov.tw'
    ),
    4225: AppConfig(
        appid=4225,
        appname='4225_ctv',
        appclass=parser.TwCtvParser,
        appdomain='new.ctv.com.tw'
    ),
    4226: AppConfig(
        appid=4226,
        appname='4226_moigov',
        appclass=parser.TwMoigovParser,
        appdomain='www.moi.gov.tw'
    ),
    4227: AppConfig(
        appid=4227,
        appname='4227_hsinchu',
        appclass=parser.TwHsincHuParser,
        appdomain='www.hsinchu.gov.tw'
    ),
    4228: AppConfig(
        appid=4228,
        appname='4228_afpc',
        appclass=parser.TwAfpcParser,
        appdomain='afpc.mnd.gov.tw'
    ),
    4229: AppConfig(
        appid=4229,
        appname='4229_cga',
        appclass=parser.TwCgaParser,
        appdomain='www.cga.gov.tw'
    ),
    4230: AppConfig(
        appid=4230,
        appname='4230_klcg',
        appclass=parser.TwKlcgParser,
        appdomain='www.klcg.gov.tw'
    ),
    4231: AppConfig(
        appid=4231,
        appname='4231_mof',
        appclass=parser.TwMofParser,
        appdomain='www.mof.gov.tw'
    ),
    4232: AppConfig(
        appid=4232,
        appname='4232_taiwannet',
        appclass=parser.TwTaiwanneTParser,
        appdomain='news.taiwannet.com.tw'
    ),
    4233: AppConfig(
        appid=4233,
        appname='4233_anntw',
        appclass=parser.TwAnntwParser,
        appdomain='anntw.com'
    ),
    4234: AppConfig(
        appid=4234,
        appname='4234_people',
        appclass=parser.CnPeoPleParser,
        appdomain='japan.people.com.cn'
    ),
    4235: AppConfig(
        appid=4235,
        appname='4235_setn',
        appclass=parser.TwSetnParser,
        appdomain='www.setn.com'
    ),
    4237: AppConfig(
        appid=4237,
        appname='4237_cnyes',
        appclass=parser.TwCnyesParser,
        appdomain='news.cnyes.com'
    ),
    4238: AppConfig(
        appid=4238,
        appname='4238_fsr',
        appclass=parser.TwFsrParser,
        appdomain='www.fsr.com.tw'
    ),
    # 4239: AppConfig(
    #     appid=4239,
    #     appname='4239_npforg',
    #     appclass=parser.TwNpforgParser,
    #     appdomain='www.npf.org.tw'
    # ),
    4240: AppConfig(
        appid=4240,
        appname='4240_hccg',
        appclass=parser.TwHccgParser,
        appdomain='www.hccg.gov.tw'
    ),
    4236: AppConfig(
        appid=4236,
        appname='4236_beyondnews852',
        appclass=parser.HkBeyondnews852Parser,
        appdomain='beyondnews852.com'
    ),
    4242: AppConfig(
        appid=4242,
        appname='4242_tibet',
        appclass=parser.TwTibeTParser,
        appdomain='www.tibet.org.tw'
    ),
    4243: AppConfig(
        appid=4243,
        appname='4243_cnews',
        appclass=parser.TwCnewsParser,
        appdomain='cnews.com.tw'
    ),
    4249: AppConfig(
        appid=4249,
        appname='4249_skypost',
        appclass=parser.HkSkypoStParser,
        appdomain='skypost.ulifestyle.com.hk'
    ),
    4250: AppConfig(
        appid=4250,
        appname='4250_cnkmgroup',
        appclass=parser.TwCnkmgroupParser,
        appdomain='cnkmgroup.com'
    ),
    5070:AppConfig(
        appid=5070,
        appname='5070_thenewslens',
        appclass=parser.TwThenewslensParser,
        appdomain='www.thenewslens.com'
    ),
    5071:AppConfig(
        appid=5071,
        appname='5071_savantas',
        appclass=parser.HkSavantaSParser,
        appdomain='www.savantas.org'
    ),
    5072:AppConfig(
        appid=5072,
        appname='5072_hkzmi',
        appclass=parser.HkHkzmiParser,
        appdomain='www.hkzmi.com'
    ),
    4251: AppConfig(
        appid=4251,
        appname='4251_rand',
        appclass=parser.UsaRandParser,
        appdomain='www.rand.org'
    ),
    4252: AppConfig(
        appid=4252,
        appname='4252_ipsdc',
        appclass=parser.UsaIpsdcParser,
        appdomain='ips-dc.org'
    ),
    4253: AppConfig(
        appid=4253,
        appname='4253_tyenews',
        appclass=parser.TwTyenewsParser,
        appdomain='tyenews.com'
    ),
    5074:AppConfig(
        appid=5074,
        appname='5074_law_moj',
        appclass=parser.TwLaw_mojParser,
        appdomain='law.moj.gov.tw'
    ),
    5073:AppConfig(
        appid=5073,
        appname='5073_c4isrnet',
        appclass=parser.UsaC4isrnetParser,
        appdomain='www.c4isrnet.com'
    ),
    4254: AppConfig(
        appid=4254,
        appname='4254_yunlin',
        appclass=parser.TwYunlinParser,
        appdomain='www.yunlin.gov.tw'
    ),
    4255: AppConfig(
        appid=4255,
        appname='4255_ourhkfoundation',
        appclass=parser.HkOurhkfOundatiOnParser,
        appdomain='www.ourhkfoundation.org.hk'
    ),
    4256: AppConfig(
        appid=4256,
        appname='4256_ncforum',
        appclass=parser.HkNcforumParser,
        appdomain='www.ncforum.org.hk'
    ),
    4257: AppConfig(
        appid=4257,
        appname='4257_llri',
        appclass=parser.LtLLriParser,
        appdomain='en.llri.lt'
    ),
    4260: AppConfig(
        appid=4260,
        appname='4260_nbr',
        appclass=parser.UsaNbrParser,
        appdomain='www.nbr.org'
    ),
    4261: AppConfig(
        appid=4261,
        appname='4261_cia',
        appclass=parser.UsaCiaParser,
        appdomain='www.cia.gov'
    ),
    4264: AppConfig(
        appid=4264,
        appname='4264_vip',
        appclass=parser.TwVipParser,
        appdomain='vip.udn.com'
    ),
    5076:AppConfig(
        appid=5076,
        appname='5076_airforcetimes',
        appclass=parser.UsaAirforcetimesParser,
        appdomain='www.airforcetimes.com'
    ),
    5077:AppConfig(
        appid=5077,
        appname='5077_hongkongwatch',
        appclass=parser.HkHongkongwatcHParser,
        appdomain='www.hongkongwatch.org'
    ),
    5078:AppConfig(
        appid=5078,
        appname='5078_ifeng',
        appclass=parser.CnIfengParser,
        appdomain='www.ifeng.com'
    ),
    4266: AppConfig(
        appid=4266,
        appname='4266_salon',
        appclass=parser.UsaSalonParser,
        appdomain='www.salon.com'
    ),
    4267: AppConfig(
        appid=4267,
        appname='4267_ciis',
        appclass=parser.CnCiisParser,
        appdomain='www.ciis.org.cn'
    ),
    4268: AppConfig(
        appid=4268,
        appname='4268_cepr',
        appclass=parser.CnCeprParser,
        appdomain='cepr.org'
    ),
    4269: AppConfig(
        appid=4269,
        appname='4269_chosun',
        appclass=parser.KpChosunParser,
        appdomain='cnnews.chosun.com'
    ),
    4270: AppConfig(
        appid=4270,
        appname='4270_yomiuri',
        appclass=parser.JpYomiuriParser,
        appdomain='www.yomiuri.co.jp'
    ),
    4271: AppConfig(
        appid=4271,
        appname='4271_sgzaobao',
        appclass=parser.SgSgzaobaoParser,
        appdomain='www.zaobao.com'
    ),
    4272: AppConfig(
        appid=4272,
        appname='4272_wrap',
        appclass=parser.TwWrapParser,
        appdomain='www.wrap.gov.tw'
    ),
    4273: AppConfig(
        appid=4273,
        appname='4273_cri',
        appclass=parser.CnCriParser,
        appdomain='news.cri.cn'
    ),
    4274: AppConfig(
        appid=4274,
        appname='4274_bitterwinter',
        appclass=parser.ItBitterwinterParser,
        appdomain='zh.bitterwinter.org'
    ),
    4275: AppConfig(
        appid=4275,
        appname='4275_cssn',
        appclass=parser.CnCssnParser,
        appdomain='ijs.cssn.cn'
    ),
    4276: AppConfig(
        appid=4276,
        appname='4276_cpps',
        appclass=parser.MyCppsParser,
        appdomain='cpps.org.my'
    ),
    4277: AppConfig(
        appid=4277,
        appname='4277_tdri',
        appclass=parser.ThTdriParser,
        appdomain='tdri.or.th'
    ),
    4278: AppConfig(
        appid=4278,
        appname='4278_rosstat',
        appclass=parser.RuRosstatParser,
        appdomain='rosstat.gov.ru'
    ),
    4279: AppConfig(
        appid=4279,
        appname='4279_pircenter',
        appclass=parser.RuPircenterParser,
        appdomain='pircenter.org'
    ),
    4280: AppConfig(
        appid=4280,
        appname='4280_carnegiemoscow',
        appclass=parser.RuCarnegiemosCowParser,
        appdomain='carnegiemoscow.org'
    ),
    4281: AppConfig(
        appid=4281,
        appname='4281_levada',
        appclass=parser.RuLevadaParser,
        appdomain='www.levada.ru'
    ),
    4282: AppConfig(
        appid=4282,
        appname='4282_razumkov',
        appclass=parser.UaRazumkovParser,
        appdomain='razumkov.org.ua'
    ),
    4283: AppConfig(
        appid=4283,
        appname='4283_vass',
        appclass=parser.VnVassParser,
        appdomain='www.vass.gov.vn'
    ),
    4284: AppConfig(
        appid=4284,
        appname='4284_govkg',
        appclass=parser.KgGovkGParser,
        appdomain='www.gov.kg'
    ),
    4285: AppConfig(
        appid=4285,
        appname='4285_northwesternmutual',
        appclass=parser.UsaNorthwesterNmutualParser,
        appdomain='news.northwesternmutual.com'
    ),
    4286: AppConfig(
        appid=4286,
        appname='4286_fema',
        appclass=parser.UsaFemaParser,
        appdomain='www.fema.gov'
    ),
    4287: AppConfig(
        appid=4287,
        appname='4287_sef',
        appclass=parser.TwSefParser,
        appdomain='www.sef.org.tw'
    ),
    4288: AppConfig(
        appid=4288,
        appname='4288_kairos',
        appclass=parser.TW_kairosParser,
        appdomain='kairos.news'
    ),
    4289: AppConfig(
        appid=4289,
        appname='4289_ettoday',
        appclass=parser.TwForum_ettodayParser,
        appdomain='forum.ettoday.net'
    ),
    5079:AppConfig(
        appid=5079,
        appname='5079_tdcpress',
        appclass=parser.TwTdcpressParser,
        appdomain='www.tdcpress.com'
    ),
    5080:AppConfig(
        appid=5080,
        appname='5080_montsame',
        appclass=parser.MnMontsaMeParser,
        appdomain='montsame.mn'
    ),
    5081:AppConfig(
        appid=5081,
        appname='5081_theubposts',
        appclass=parser.MnTheubposTsParser,
        appdomain='theubposts.com'
    ),
    5082:AppConfig(
        appid=5082,
        appname='5082_mminfo',
        appclass=parser.MnMMinfoParser,
        appdomain='www.mminfo.mn'
    ),
    5083:AppConfig(
        appid=5083,
        appname='5083_zms',
        appclass=parser.MnZmsParser,
        appdomain='www.zms.mn'
    ),
    5084:AppConfig(
        appid=5084,
        appname='5084_dailynews',
        appclass=parser.MnDailynewsParser,
        appdomain='dailynews.mn'
    ),
    4290: AppConfig(
        appid=4290,
        appname='4290_apnews',
        appclass=parser.MnApnewsParser,
        appdomain='apnews.com'
    ),
    4291: AppConfig(
        appid=4291,
        appname='4291_ikon',
        appclass=parser.MnIkonParser,
        appdomain='ikon.mn'
    ),
    4292: AppConfig(
        appid=4292,
        appname='4292_gandan',
        appclass=parser.MnGandanParser,
        appdomain='gandan.mn'
    ),
}
