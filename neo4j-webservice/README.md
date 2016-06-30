# Neo4j database backend

Import the data files in the `csv` folder to your local Neo4j database using the folowing command.

`neo4j-import --into db_wdm/ --nodes:MOVIE csv/movies_node.csv --nodes:ACTOR csv/actors_node.csv --nodes:GENRE csv/genres_nodes.csv --nodes:KEYWORD csv/keywords_nodes.csv --nodes:AKA_TITLE csv/aka_titles_nodes.csv --nodes:AKA_NAME csv/aka_names_nodes.csv --nodes:SERIES csv/series_nodes.csv --relationships:aka_name csv/aka_names_rels.csv --relationships:aka_title csv/aka_titles_rels.csv --relationships:has_genre csv/movies_genres_rels.csv --relationships:has_keyword csv/movies_keywords_rels.csv --relationships:acted_in csv/acted_in_rels.csv --relationships:has_series csv/series_rels.csv --delimiter ";" --array-delimiter "|"`

All data files can be found [here](https://drive.google.com/open?id=0B-P82zGOa634SnNjTmxJUng5U2c).