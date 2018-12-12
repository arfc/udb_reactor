import sqlite3 as lite
import os
import pandas as pd
import numpy as np

""" This script generates two cyclus input files:
  one where the recipe is used, and the other using the udb database

  Separate xml files are created for simplicity, and XInclude is used."""

db_path = '/home/teddy/github/udb_reactor/db/1yr.dat'
output_path = 'input.xml'
recipe_output_path = 'recipe_input.xml'

df = pd.read_table(db_path)
id_list = df['reactor_id'].unique()

# start year is 1969-01
xml_file = """
<simulation xmlns:xi="http://www.w3.org/2001/XInclude">

  <archetypes>
    <spec>
      <lib>agents</lib>
      <name>NullRegion</name>
    </spec>
    <spec>
      <lib>agents</lib>
      <name>NullInst</name>
    </spec>
    <spec>
      <lib>cycamore</lib>
      <name>Sink</name>
    </spec>
    <spec>
      <lib>cycamore</lib>
      <name>DeployInst</name>
    </spec>
    <spec>
      <lib>cycamore</lib>
      <name>Storage</name>
    </spec>
    <spec>
      <lib>udb_reactor.udb_reactor</lib>
      <name>udb_reactor</name>
    </spec>
  </archetypes>

  <control>
    <!-- 2020/07 - 1969/01 -->
    <duration>619</duration>
    <startmonth>1</startmonth>
    <startyear>1969</startyear>
    <decay>lazy</decay>
  </control>


"""

archetype_file = "<root>"
for reactor_id in id_list:
    archetype_file += """
    <facility>
        <config>
          <udb_reactor>
            <outcommod>fuel</outcommod>
            <reactor_id>%i</reactor_id>
            <db_path>%s</db_path>
            <recipe_name>used_fuel_recipe</recipe_name>
            <startyear>1969</startyear>
            <startmonth>1</startmonth>
          </udb_reactor>
        </config>
        <name>%i</name>
    </facility>
    """ %(reactor_id, db_path, reactor_id)

archetype_file += "</root>"
with open('./archetype_recipe.xml', 'w') as f:
    f.write(archetype_file)

archetype_without_recipe = archetype_file.replace('<recipe_name>used_fuel_recipe</recipe_name>\n', '')
with open('./archetype.xml', 'w') as f:
    f.write(archetype_without_recipe)


xml_file += """

  <xi:include href="./archetype_recipe.xml" xpointer="xpointer(/root/facility)"/>

    <facility>
        <name>storage</name>
        <config>
            <Storage>
                <in_commods>
                    <val>fuel</val>
                </in_commods>
                <out_commods>
                    <val>fuel_decayed</val>
                </out_commods>
            </Storage>
        </config>
    </facility>


    <facility>
        <name>sink</name>
        <config>
            <Sink>
                <in_commods>
                    <val>fuel_decayed</val>
                </in_commods>
                <capacity>1e299</capacity>
            </Sink>
        </config>
    </facility>

"""

xml_file += """

<region>
    <name>SingleRegion</name>
    <config><NullRegion/></config>
    <institution>
      <name>udb_reactor_inst</name>
      <initialfacilitylist>
      <entry>
        <prototype>storage</prototype>
        <number>1</number>
      </entry>
"""

entry_file = "<root>"
for reactor_id in id_list:
    entry_file += """
        <entry>
          <prototype>%i</prototype>
          <number>1</number>
        </entry>
    """ %reactor_id
entry_file += "</root>"
with open('prototype.xml', 'w') as f:
    f.write(entry_file)

xml_file += """
      <xi:include href="./prototype.xml" xpointer="xpointer(/root/entry)"/>
      </initialfacilitylist>
      <config>
      <NullInst/>
      </config>
    </institution>
     <institution>
            <name>fac</name>
            <config>
                <DeployInst>
                    <prototypes>
                        <val>sink</val>
                    </prototypes>
                    <build_times>
                        <val>617</val>
                    </build_times>
                    <n_build>
                        <val>1</val>
                   </n_build>
                    <lifetimes>
                        <val>9999</val>
                    </lifetimes>
                </DeployInst>
            </config>
        </institution>
  </region>
"""

xml_file += """<xi:include href="avg_recipe.xml" xpointer="xpointer(/root/recipe)"/>
            </simulation>"""


with open(recipe_output_path, 'w') as f:
    f.write(xml_file)

xml_file_without_recipe = xml_file.replace('<xi:include href="./archetype_recipe.xml" xpointer="xpointer(/root/facility)"/>',
                                           '<xi:include href="./archetype.xml" xpointer="xpointer(/root/facility)"/>')
xml_file_without_recipe = xml_file_without_recipe.replace('<xi:include href="avg_recipe.xml" xpointer="xpointer(/root/recipe)"/>',
                                                          '')

with open(output_path, 'w') as f:
    f.write(xml_file_without_recipe)


mean_burnup = np.mean(df['discharge_burnup'].unique())
mean_enrichment = np.mean(df['initial_enrichment'].unique())
df['bu_diff'] = np.abs(df['discharge_burnup'] - mean_burnup)
df['er_diff'] = np.abs(df['initial_enrichment'] - mean_enrichment)
df['tot_diff'] = np.abs(df['bu_diff'] + df['er_diff'])
indx = df['tot_diff'].argmin()
assem_id = df.loc[indx, 'assembly_id']
comp = df.loc[df['assembly_id'] == assem_id][['name', 'total_mass_g']]
tot_mass = sum(comp['total_mass_g'])
with open('avg_recipe.xml', 'w') as f:
    head = "<root>\n<recipe>\n\t<name>used_fuel_recipe</name>\n\t<basis>mass</basis>\n"
    for indx, row in comp.iterrows():
        head += '\t\t<nuclide> <id>%s</id> <comp>%f</comp> </nuclide>\n' % (
                    row['name'].capitalize(), float(row['total_mass_g'])  / tot_mass)
    head += '</recipe></root>'
    f.write(head)

print('DONE!')
