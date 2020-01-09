if [ $# -eq 1 ]
then
    http get localhost:8000/api/tournaments/$1
else
    echo "Usage:./httpie_test_get_tournament.sh <tournament_id>"
fi
