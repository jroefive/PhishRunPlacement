import pandas as pd
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.transform import jitter, linear_cmap
from bokeh.models import ColorBar
from bokeh.palettes import RdYlBu11

#Get Tracks
tracks = pd.read_csv('pecent_into_show')

#Filter down to just tours that are 4 shows long
four_runs = tracks[tracks['shows_count'] == 4]

#Get dates and tour ids to clean up the final list of shows
dates = four_runs.date.unique()
tours = four_runs.tour_id.unique()
dates = sorted(dates)

#Dates to add and drop
add_dates = ['2002-12-31', '2003-01-02', '2003-01-03', '2003-01-04', '2018-12-28', '2018-12-29', '2018-12-30', '2018-12-31']
drop_dates = ['2000-05-15', '2000-05-16', '2000-05-18', '2000-05-19', '2004-08-09', '2004-08-10', '2004-08-11', '2004-08-12', '2009-10-30', '2009-10-31', '2009-11-01', '2011-07-01', '2011-07-02', '2011-07-03', '2019-02-21', '2019-02-22', '2019-02-23']

#Add and drop dates
dates_final = [x for x in dates if x not in drop_dates]
for date in add_dates:
    dates_final.append(date)



#Filter df down to just shows in 4 night runs
final_runs = tracks[tracks.date.isin(dates_final)]

#Create a column for show number
show_numbers = [1,2,3,4]*22
tuples = list(zip(dates_final, show_numbers))
show_number_df = pd.DataFrame(tuples, columns=['date','show_number'])
final_runs = pd.merge(final_runs,show_number_df,on='date', how='left')

#Createa column for placement, year, and hover for graph
final_runs['placement'] = final_runs['show_number'] + final_runs['percentintoshow']
final_runs['year'] = pd.DatetimeIndex(final_runs['date']).year
final_runs['percent'] = round(final_runs['percentintoshow']*100,0)
final_runs['hover'] = final_runs['percent'].astype(str) + '% into show number ' + final_runs['show_number'].astype(str)


#Get counts of how many times songs have been played during 4 night runs
counts = final_runs.groupby('title').count()
counts = counts.sort_values(by=['id'], ascending=False)

#Create lists of ten songs each for graphing
top10 = counts.head(10)
top10 = top10.index.values
top20 = counts.head(20)
top20a = top20.index.values
top20 = [x for x in top20a if x not in top10]
top30 = counts.head(30)
top30a = top30.index.values
top30 = [x for x in top30a if x not in top20a]
top40 = counts.head(40)
top40a = top40.index.values
top40 = [x for x in top40a if x not in top30a]

#Get list of years for color mapping
years = final_runs['year'].values
mapper = linear_cmap(field_name='year', palette=RdYlBu11, low=min(years) ,high=max(years))

#Set up the hover layout
TOOLTIPS = [('Date', '@date'), ('Placement', '@hover')]

#Create a source for graphing
source = ColumnDataSource(data=final_runs)


#Create figure
p = figure(y_range = top10, title='Song Placement During Stand-Alone 4 Night Runs - 10 Most Played', tooltips=TOOLTIPS)
p.circle(x='placement', y=jitter('title', width = 0.2, range=p.y_range), radius = 0.05, fill_alpha=0.6, source = source,
        color=mapper)

#Change x axis lables
p.xaxis.major_label_overrides = {1: "Show 1", 2: "Show 2", 3: "Show 3", 4: 'Show 4', 5:'Back to Real Life'}
p.xaxis.axis_label = "All NYE runs (w/o Cypress or 2011/12), Island Tour, 20th Anniversary, and Mexico2020"

#Create stripes
p.xgrid.band_hatch_pattern = "/"
p.xgrid.band_hatch_alpha = 0.6
p.xgrid.band_hatch_color = "lightgrey"
p.xgrid.band_hatch_weight = 0.5
p.xgrid.band_hatch_scale = 10

#Add color bar
color_bar = ColorBar(color_mapper=mapper['transform'], width=8,  location=(0,0))
p.add_layout(color_bar, 'right')

#Save and show
output_file("scatter10.html")
show(p)

