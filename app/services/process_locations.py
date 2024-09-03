import collections


def group_locations_by_zip(locations):
    zip_dict = collections.defaultdict(lambda: {"zip_code": "", "state_id": ""})

    for location in locations:
        zip_code = location["zip"]
        state_id = location["state_id"]
        city = location["city"]
        county = location["county_name"]
        county_fips = location["county_fips"]

        zip_dict[zip_code]["zip_code"] = zip_code
        zip_dict[zip_code]["state_id"] = state_id
        zip_dict[zip_code]["city"] = city
        zip_dict[zip_code]["county"] = county
        zip_dict[zip_code]["county_fips"] = county_fips

    return zip_dict
