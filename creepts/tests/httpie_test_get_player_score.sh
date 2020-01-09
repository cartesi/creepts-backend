if [ $# -eq 2 ]
then
    http get localhost:8000/api/tournaments/$1/scores/$2
else
    echo "Usage:./httpie_test_get_player_score.sh <tournament_id> <player_id>"
fi
