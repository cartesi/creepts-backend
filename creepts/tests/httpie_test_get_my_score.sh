if [ $# -eq 1 ]
then
    http get localhost:8000/api/tournaments/$1/scores/my
else
    echo "Usage:./httpie_test_get_my_score.sh <tournament_id>"
fi
