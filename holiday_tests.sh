for run in run1 #run2 run3 run4 run5
do
	for pattern in long_equal #small_equal peaks
	do
		echo $pattern $run without
		artillery run demo/artillery/new_patterns/$pattern.yml -o results2/$pattern/without_tuner/$run/artillery.out

		echo $pattern $run with
		python3 TopologyGenerator/main.py TopologyGenerator/settings-php_apache.json -l results2/$pattern/with_tuner/$run/tuner.log &
		artillery run demo/artillery/new_patterns/$pattern.yml -o results2/$pattern/with_tuner/$run/artillery.out
		killall python3

		echo $pattern $run with_no_node_removal
		python3 TopologyGenerator/main.py TopologyGenerator/settings-php_apache_no_node_removal.json -l results2/$pattern/with_tuner_no_node_removal/$run/tuner.log &
		artillery run demo/artillery/new_patterns/$pattern.yml -o results2/$pattern/with_tuner_no_node_removal/$run/artillery.out
		killall python3
	done
done
make down-demo
