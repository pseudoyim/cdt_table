'''
Scrapes CDT package namespaces and tabulates them (for inventory/survey purposes)

Steps:
    1. Pull repodata from channels and searches for packages ending with the CDT suffixes (OS-ARCH).
    2. Make a df with an index column of just the CDT names (e.g. "libx11-devel").
    3. Iteratively LEFT JOIN all of the suffixes' CDT names onto the index column.
'''
import pandas as pd
import requests

# This dict maps a channel to the CDT suffixes one can expect
# to find in that channel. For example:
#   "channel": ["CDT suffix1", "CDT suffix2"]
CHANNEL_CDT_MAPPING = {
    'anaconda': ['cos6-i686', 
                 'cos6-x86_64', 
                 'cos7-x86_64', 
                 'cos7-ppc64le', 
                 'cos7-s390x'],
    'aarch64-staging': ['amzn2-aarch64']
    }


def main(output_csv_path):
    final = {}
    unique_cdt_names = set()

    # 1. Pull repodata from channels and searches for packages ending with the CDT suffixes (OS-ARCH).
    # Scrape repodata (CDTs are all in noarch subdir) for "name" value.
    for channel, cdt_suffixes in CHANNEL_CDT_MAPPING.items():

        suffix_namespaces = {}

        if channel == 'anaconda':
            repodata_url = 'https://repo.anaconda.com/pkgs/main/noarch/repodata.json'
        else:
            repodata_url = f'https://conda.anaconda.org/{channel}/noarch/repodata.json'
    
        response = requests.get(repodata_url)
        response_dict = dict(response.json())

        # 'packages' is a dict of dicts.
        packages = response_dict['packages']

        for pkg, pkg_info in packages.items():

            # 'pkg' is a dict.
            namespace = pkg_info['name']
        
            for suffix in cdt_suffixes:
                if suffix in namespace:
                    
                    # Separate the suffix from the CDT name.
                    # e.g. gtk2-amzn2-aarch64 becomes:
                    #   cdt_name == 'gtk2'
                    #   suffix == 'amzn2_aarch64'
                    cdt_name = namespace.split(f'-{suffix}')[0]
                    
                    if suffix not in suffix_namespaces:
                        suffix_namespaces[suffix] = {cdt_name}
                    else:
                        suffix_namespaces[suffix].add(cdt_name)
                    unique_cdt_names.add(cdt_name)

        final.update(suffix_namespaces)

    # 2. Make a df with an index column of just the unique CDT names.
    all_cdt_names = list(unique_cdt_names)
    df = pd.DataFrame(all_cdt_names, columns=['CDT_name'])

    # 3. Iteratively LEFT JOIN all of the suffixes' CDT names onto the index column.
    for suffix, suf_cdt_names in final.items():
        # print(suf_cdt_names)
        df_temp = pd.DataFrame(list(suf_cdt_names), columns=[suffix])
        
        print(df_temp)
        df = df.merge(df_temp, how='left', left_on='CDT_name', right_on=suffix)

    df = df.sort_values('CDT_name')
    print(df)
    # Dump to csv.
    df.to_csv(output_csv_path, index=False)
        





if __name__ == '__main__':

    output_csv_path = '~/Desktop/cdt_info.csv'
    main(output_csv_path)
