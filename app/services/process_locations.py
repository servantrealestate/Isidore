import collections


def group_locations_by_county(locations):
    county_dict = collections.defaultdict(lambda: {"county_name": "", "zipcodes": []})

    for location in locations:
        county_fips = location["county_fips"]
        county_name = location["county_name"]
        state_id = location["state_id"]
        zipcode = location["zip"]

        county_dict[county_fips]["county_name"] = county_name
        county_dict[county_fips]["state_id"] = state_id
        county_dict[county_fips]["zipcodes"].append(zipcode)

    return county_dict
