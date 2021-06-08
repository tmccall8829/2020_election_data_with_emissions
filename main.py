import pandas as pd
import plotly.express as px
import us

votes_df = pd.read_csv("/Users/tom/Library/Mobile Documents/com~apple~CloudDocs/Programming/data/1976-2020-president.csv")
pop_df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv")
emissions_df = pd.read_csv("/Users/tom/Library/Mobile Documents/com~apple~CloudDocs/Programming/data/Total Carbon Dioxide Emissions-StateRankings.csv")

# remove PR and DC from population df and reset the index
pop_df = pop_df.loc[(pop_df.Postal != "PR") & (pop_df.Postal != "DC")].reset_index()
pop_df.loc[:, "State"] = pop_df.State.apply(lambda x: x.upper())

# map the state abbreviations to their full names
emissions_df.loc[:, 'State'] = emissions_df.State.apply(lambda x: us.states.lookup(x).name.upper())
emissions_df.rename(columns={"Total Carbon Dioxide Emissions, million metric tons": "MMTCO2e"}, inplace=True)
emissions_df_filtered = emissions_df[["State", "MMTCO2e"]].loc[emissions_df.State != "DISTRICT OF COLUMBIA"]

# create new col, voteperc, which is that candidate's state voteshare in percent
votes_df["voteperc"] = votes_df["candidatevotes"] / votes_df["totalvotes"]

# keep Biden and Trump 2020 results
votes_df_filtered = votes_df.loc[(votes_df.year == 2020) &
                    (votes_df.writein == False) &
                    ((votes_df.party_simplified == "DEMOCRAT") | (votes_df.party_simplified == "REPUBLICAN"))]

# only keep the columns we really want, to keep the df small
votes_df_filtered_shrunk = votes_df_filtered[["year",
                                              "state",
                                              "state_po",
                                              "state_fips",
                                              "candidatevotes",
                                              "totalvotes",
                                              "voteperc",
                                              "party_simplified"]]

# split into two dfs to subtract from each other
votes_dems = votes_df_filtered_shrunk.loc[votes_df_filtered_shrunk.party_simplified == "DEMOCRAT"]
votes_gop = votes_df_filtered_shrunk.loc[votes_df_filtered_shrunk.party_simplified == "REPUBLICAN"]

# subtract DEM FROM GOP so that states that biden won are negative (on the "left")
vote_swing = list(votes_gop.set_index("state").voteperc.subtract(votes_dems.set_index("state").voteperc) * 100)

final_votes_df = pd.DataFrame()
final_votes_df["vote_swing"] = vote_swing
final_votes_df["State"] = votes_gop.state.unique()
final_votes_df = final_votes_df.merge(emissions_df_filtered, on="State", how='outer')
final_votes_df = final_votes_df.merge(pop_df, on="State", how="outer")
final_votes_df["size_factor"] = final_votes_df["MMTCO2e"] / final_votes_df["Population"]

fig = px.scatter(
    final_votes_df,
    x="vote_swing",
    y="State",
    text="Postal",
    range_x=[-50, 50],
    color="vote_swing",
    color_continuous_scale=px.colors.diverging.balance,
    size="size_factor",
    size_max=80
)

fig.update_yaxes(
    showticklabels=False,
    title=""
)

fig.update_xaxes(
    title="",
    tickmode="array",
    tickvals=[-45, -30, -15, 15, 30, 45],
    ticktext=["+45 Biden", "+30 Biden", "+15 Biden", "+15 Trump", "+30 Trump", "+45 Trump"]
)

fig.update_layout(
    coloraxis_showscale=False,
    title="2020 Presidential Election Turnout, Scaled by State Emissions Per Person",
    paper_bgcolor='rgba(255,255,255,100)',
    plot_bgcolor='rgba(255,255,255,100)'
)

fig.show()
