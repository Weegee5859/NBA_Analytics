import requests
import os
from bs4 import BeautifulSoup
from dash import Dash, html
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

teams = []

def loadTeams():
	# Attempt to load team names txt file
	try:
		with open('team_names.txt') as txt_file:
			for line in txt_file:
				teams.append(line.strip())
	except:
		print("File could not be found!")
	# Print all the teams
	for team in teams:
		print(team)

def returnNbaPlayerData(team_name):
	# Load the FINAL random page
	URL = "https://www.basketball-reference.com/teams/"+team_name+"/2023.html#all_roster"
	try:
		r = requests.get(URL)
	except:
		print("Could not get team's data!")
		return None
	soup = BeautifulSoup(r.content, 'html5lib')

	# Get all the recipes on the current page
	statsTable = soup.find(class_="stats_table")

	if not statsTable:
		print("Data could not be found for this team!")
		return None

	results = []

	for row in statsTable.findAll('tr'):
		player_data = {}
		for cell in row.findAll('td'):
			stat_name = cell.get("data-stat")
			stat_text = cell.text
			if not stat_name or not stat_text:
				continue
			player_data[stat_name] = stat_text
		if player_data:
			results.append(player_data.copy())
	return results

def returnFormattedPlayerData(player_data):
	data = {"Players": [], "Position": [], "Height": [], "Weight": [], "Birth Date": [], "Birth Country": [], "Years Experience": []}
	for player in player_data:
		data["Players"].append(player["player"])
		data["Position"].append(player["pos"])
		data["Height"].append(float(player["height"].replace("-",".")))
		data["Weight"].append(float(player["weight"]))
		data["Birth Date"].append(player["birth_date"])
		data["Birth Country"].append(player["birth_country"].capitalize())
		data["Years Experience"].append(player["years_experience"])
		print("-----------------------------------")
	return data

def inputTeamName():
	while(True):
		print("Type in the 3 letter abbreviations to display that teams Player stats.")
		my_input = input()
		# Input has to be at least 3 characters
		if len(my_input) != 3:
			print("Input must be 3 letters.")
			continue
		for team in teams:
			# if input matches the first 3 letters of team name
			# Return the team name
			if my_input.lower() in team[:4].lower():
				print(str(my_input).upper())
				return str(my_input).upper()
		print("invalid team name.")


def displayTeamsData():

	team_name = inputTeamName()

	#Scrape Player Data
	player_data = returnNbaPlayerData(team_name)
	if not player_data: return
	print(player_data)
	#Format Player Data for Plotly
	player_data_plot = returnFormattedPlayerData(player_data)
	if not player_data_plot: return
	print(player_data_plot)

	# Configure Plotly Graph
	fig = make_subplots(rows=3, cols=1,specs=[
	    	[{"type": "table"}],
	    	[{"type": "bar"}],
	    	[{"type": "bar"}]
	    ]
	)

	fig.add_trace(
		go.Bar(x=player_data_plot['Players'], y=player_data_plot["Weight"],name="Player Weight"),
		row=3,col=1
	)

	fig.add_trace(
		go.Bar(x=player_data_plot['Players'], y=player_data_plot["Height"],name="Player Height"),
		row=2,col=1
	)


	nba_table = data=go.Table(
			header=dict(values=['Players', 'Position', 'Birth Date','Birth Country','Years Experience']),
			cells=dict(values=[
				player_data_plot['Players'],
				player_data_plot['Position'],
				player_data_plot['Birth Date'],
				player_data_plot['Birth Country'],
				player_data_plot['Years Experience']
			])
		)

	fig.add_trace(nba_table,row=1,col=1)
	fig.update_layout(height=800, width=1000, title_text="NBA Team Data")
	fig.show()

loadTeams()
while True:
	displayTeamsData()