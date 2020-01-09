if [ $# -eq 2 ]
then
    http put localhost:8000/api/tournaments/$1/scores/my content-type:application/json < $2
else
    echo "Usage:./httpie_test_put_my_score.sh <tournament_id> <payload_json_filename>"
fi
