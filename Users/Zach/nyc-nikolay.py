import pandas as pd

def get_output_path_from_s3_url(s3_url):
    """
    transform s3 output path (from beam runs spreadsheet) into path to s3 output
    that may be used as part of path to the file.

    s3path = get_output_path_from_s3_url(s3url)
    beam_log_path = s3path + '/beamLog.out'
    """

    return s3_url \
        .strip() \
        .replace("s3.us-east-2.amazonaws.com/beam-outputs/index.html#", "beam-outputs.s3.amazonaws.com/")


def label_mta_bridge_tunnel_crossings(pte):
    henry_hudson_bridge = {1681043, 1681042, 542015, 542014, 88230, 88231} #
    robert_f_kennedy_bridge = {1235912, 1235913, 1247588, 1247589, 21094, 21095, 23616, 23617, 29774, 29775, 30814,
                               30815, 763932, 763933, 782436, 782437, 782438, 782439, 782440, 782441, 782560, 782561,
                               782570, 782571, 782702, 782703, 782706, 782707, 782708, 782709, 782718, 782719, 870348,
                               870349, 782720, 782721, 782722, 782723, 782724, 782725, 782726, 782727, 782728, 782729,
                               782914, 782915, 853900, 853901, 1230075, 1233314, 1233315, 1299262, 1299263, 1299264,
                               1299265, 1299266, 1299267, 1299268, 1299269, 1299274, 1299275, 1299278, 1299279, 958834,
                               958835, 958836, 958837, 916655, 1041132, 1041133, 1078046, 1078047, 1078048, 1078049,
                               1078050, 1078051, 1078052, 1078053, 1078056, 1078057, 1078058, 1078059, 1078060, 1078061,
                               1089632, 1089633, 1089634, 1089635, 1101864, 1101865, 1101866, 1101867, 1230068, 1230069,
                               1230070, 1230071, 1230072, 1230073, 1230074, 916652, 916653, 916654, 757589, 757588,
                               853929, 853928, 779898, 779899, 1339888, 1339889, 1339890, 1339891, 1433020, 1433021,
                               154, 155, 731748, 731749, 731752, 731753, 731754, 731755, 731766, 731767, 731768, 731769,
                               731770, 731771, 731786, 731787, 853892, 853893, 868400, 868401, 868410, 868411} #
    queens_midtown_tunnel = {1367889, 1367888, 487778, 487779} #X
    hugh_l_carey_tunnel = {1071576, 1071577, 1109400, 1109401, 13722, 13723, 1658828, 1658829, 19836, 19837} #
    bronx_whitestone_bridge = {62416, 62417, 729848, 729849, 765882, 765883, 853914, 853915} #
    throgs_neck_bridge = {1090614, 1090615, 1090616, 1090617, 1090618, 1090619, 765880, 765881} #
    varrazzano_narrows_bridge = {788119, 788118, 1341065, 1341064, 788122, 788123, 788140, 788141} #
    marine_parkwaygil_hodges_memorial_bridge = {1750240, 1750241, 53416, 53417, 732358, 732359, 761184, 761185, 761186,
                                                761187, 793744, 793745} #
    cross_bay_veterans_memorial_bridge = {1139186, 1139187, 1139198, 1139199, 1139200, 1139201, 1139208, 1139209,
                                          1139214, 1139215, 1139222, 1139223, 1139300, 1139301, 1139302, 1139303,
                                          1517804, 1517805, 1517806, 1517807, 1517808, 1517809, 1743514, 1743515,
                                          1749330, 1749331, 1749332, 1749333, 48132, 48133, 51618, 51619, 51620, 51621,
                                          59452, 59453, 68364, 68365, 793786, 793787, 865036, 865037, 865060, 865061,
                                          865062, 865063, 953766, 953767, 953768, 953769, 999610, 999611, 999626,
                                          999627, 999628, 999629, 1297379}#

    mta_bridges_tunnels_links = henry_hudson_bridge \
        .union(robert_f_kennedy_bridge) \
        .union(queens_midtown_tunnel) \
        .union(hugh_l_carey_tunnel) \
        .union(bronx_whitestone_bridge) \
        .union(throgs_neck_bridge) \
        .union(varrazzano_narrows_bridge) \
        .union(marine_parkwaygil_hodges_memorial_bridge) \
        .union(cross_bay_veterans_memorial_bridge)

    def car_by_mta_bridges_tunnels(row):
        if pd.isnull(row['links']):
            return False

        for link_str in row['links'].split(","):
            link = int(link_str)
            if link in mta_bridges_tunnels_links:
                return True

        return False

    pte['carMtaRelated'] = pte.apply(car_by_mta_bridges_tunnels, axis=1)

    return pte

def read_nyc_ridership_counts_absolute_numbers_for_mta_comparison(s3url, iteration=0):
    # holland_tunnel = {1110292, 1110293, 1110294, 1110295, 540918, 540919, 782080, 782081}
    # linkoln_tunnel = {1057628, 1057629, 1057630, 1057631, 308, 309, 817812, 817813, 817814, 817815, 87180, 87181}
    # george_washingtone_bridge = {735454, 735455, 767820, 767821, 781014, 781015, 781086, 781087, 781156, 781157, 782128,
    #                              782129, 796856, 796857, 796858, 796859, 796870, 796871, 866324, 866325, 87174, 87175,
    #                              87176, 87177, 88110, 88111, 886008, 886009, 968272, 968273, 781094, 781095}
    henry_hudson_bridge = {1681043, 1681042, 542015, 542014, 88230, 88231} #
    robert_f_kennedy_bridge = {1235912, 1235913, 1247588, 1247589, 21094, 21095, 23616, 23617, 29774, 29775, 30814,
                               30815, 763932, 763933, 782436, 782437, 782438, 782439, 782440, 782441, 782560, 782561,
                               782570, 782571, 782702, 782703, 782706, 782707, 782708, 782709, 782718, 782719, 870348,
                               870349, 782720, 782721, 782722, 782723, 782724, 782725, 782726, 782727, 782728, 782729,
                               782914, 782915, 853900, 853901, 1230075, 1233314, 1233315, 1299262, 1299263, 1299264,
                               1299265, 1299266, 1299267, 1299268, 1299269, 1299274, 1299275, 1299278, 1299279, 958834,
                               958835, 958836, 958837, 916655, 1041132, 1041133, 1078046, 1078047, 1078048, 1078049,
                               1078050, 1078051, 1078052, 1078053, 1078056, 1078057, 1078058, 1078059, 1078060, 1078061,
                               1089632, 1089633, 1089634, 1089635, 1101864, 1101865, 1101866, 1101867, 1230068, 1230069,
                               1230070, 1230071, 1230072, 1230073, 1230074, 916652, 916653, 916654, 757589, 757588,
                               853929, 853928, 779898, 779899, 1339888, 1339889, 1339890, 1339891, 1433020, 1433021,
                               154, 155, 731748, 731749, 731752, 731753, 731754, 731755, 731766, 731767, 731768, 731769,
                               731770, 731771, 731786, 731787, 853892, 853893, 868400, 868401, 868410, 868411} #
    queens_midtown_tunnel = {1367889, 1367888, 487778, 487779} #X
    hugh_l_carey_tunnel = {1071576, 1071577, 1109400, 1109401, 13722, 13723, 1658828, 1658829, 19836, 19837} #
    bronx_whitestone_bridge = {62416, 62417, 729848, 729849, 765882, 765883, 853914, 853915} #
    throgs_neck_bridge = {1090614, 1090615, 1090616, 1090617, 1090618, 1090619, 765880, 765881} #
    varrazzano_narrows_bridge = {788119, 788118, 1341065, 1341064, 788122, 788123, 788140, 788141} #
    marine_parkwaygil_hodges_memorial_bridge = {1750240, 1750241, 53416, 53417, 732358, 732359, 761184, 761185, 761186,
                                                761187, 793744, 793745} #
    cross_bay_veterans_memorial_bridge = {1139186, 1139187, 1139198, 1139199, 1139200, 1139201, 1139208, 1139209,
                                          1139214, 1139215, 1139222, 1139223, 1139300, 1139301, 1139302, 1139303,
                                          1517804, 1517805, 1517806, 1517807, 1517808, 1517809, 1743514, 1743515,
                                          1749330, 1749331, 1749332, 1749333, 48132, 48133, 51618, 51619, 51620, 51621,
                                          59452, 59453, 68364, 68365, 793786, 793787, 865036, 865037, 865060, 865061,
                                          865062, 865063, 953766, 953767, 953768, 953769, 999610, 999611, 999626,
                                          999627, 999628, 999629, 1297379}#

    mta_briges_tunnels_links = henry_hudson_bridge \
        .union(robert_f_kennedy_bridge) \
        .union(queens_midtown_tunnel) \
        .union(hugh_l_carey_tunnel) \
        .union(bronx_whitestone_bridge) \
        .union(throgs_neck_bridge) \
        .union(varrazzano_narrows_bridge) \
        .union(marine_parkwaygil_hodges_memorial_bridge) \
        .union(cross_bay_veterans_memorial_bridge)

    s3path = get_output_path_from_s3_url(s3url)

    # events_file_path = "{0}/ITERS/it.{1}/{1}.events.csv.gz".format(s3path, iteration)
    events_file_path = "data/nyc-may.events-4.csv.gz"
    columns = ['type', 'person', 'vehicle', 'vehicleType', 'links', 'time', 'driver']
    pte = pd.concat([df[(df['type'] == 'PersonEntersVehicle') | (df['type'] == 'PathTraversal')][columns]
                     for df in pd.read_csv(events_file_path, chunksize=100000, low_memory=False)])

    print('read pev and pt events of shape:', pte.shape)

    pev = pte[(pte['type'] == 'PersonEntersVehicle')][['type', 'person', 'vehicle', 'time']]
    pte = pte[(pte['type'] == 'PathTraversal')][['type', 'vehicle', 'vehicleType', 'links', 'time', 'driver']]

    walk_transit_modes = {'BUS-DEFAULT', 'RAIL-DEFAULT', 'SUBWAY-DEFAULT'}
    drivers = set(pte[pte['vehicleType'].isin(walk_transit_modes)]['driver'])
    pev = pev[~pev['person'].isin(drivers)]

    def get_gtfs_agency(row):
        veh_id = row['vehicle'].split(":")
        if len(veh_id) > 1:
            agency = veh_id[0]
            return agency
        return ""

    def car_by_mta_bridges_tunnels(row):
        if pd.isnull(row['links']):
            return False

        for link_str in row['links'].split(","):
            link = int(link_str)
            if link in mta_briges_tunnels_links:
                return True

        return False

    pte['carMtaRelated'] = pte.apply(car_by_mta_bridges_tunnels, axis=1)
    pte['gtfsAgency'] = pte.apply(get_gtfs_agency, axis=1)

    vehicle_info = pte.groupby('vehicle')[['vehicleType', 'gtfsAgency']].first().reset_index()

    pev_advanced = pd.merge(pev, vehicle_info, on='vehicle')
    pev_advanced = pev_advanced.sort_values('time', ignore_index=True)

    gtfs_agency_to_count = pev_advanced.groupby('gtfsAgency')['person'].count()

    # calculate car
    car_mode = {'Car', 'Car-rh-only', 'PHEV', 'BUS-DEFAULT'}
    car_mta_related = pte[(pte['vehicleType'].isin(car_mode)) &
                          (pte['carMtaRelated'])]['time'].count()
    transit_car_to_count = gtfs_agency_to_count.append(pd.Series([car_mta_related], index=['Car']))

    # calculate subway
    person_pevs = pev_advanced.groupby('person').agg(list)[['vehicleType', 'gtfsAgency']]

    def calc_number_of_subway_trips(row):
        vehicle_list = row['vehicleType']
        count_of_trips = 0
        last_was_subway = False
        for vehicle in vehicle_list:
            if vehicle == 'SUBWAY-DEFAULT':
                if not last_was_subway:
                    count_of_trips = count_of_trips + 1
                    last_was_subway = True
            else:
                last_was_subway = False
        return count_of_trips

    person_pevs['subway_trips'] = person_pevs.apply(calc_number_of_subway_trips, axis=1)
    subway_trips = person_pevs['subway_trips'].sum()

    triptype_to_count = transit_car_to_count.append(pd.Series([subway_trips], index=['Subway']))
    triptype_to_count = triptype_to_count.to_frame().reset_index()

    print('calculated:\n', pev_advanced.groupby('vehicleType')['person'].count())

    return triptype_to_count

out = read_nyc_ridership_counts_absolute_numbers_for_mta_comparison('https://s3.us-east-2.amazonaws.com/beam-outputs/index.html#output/newyork/new-york-450k-calibration-20__2022-07-12_22-31-28_czx', 10)

print(out)