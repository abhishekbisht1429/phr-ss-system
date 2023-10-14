#!/bin/bash

echo "starting influxdb daemon"
influxd &


while ! nc -z -w 5 localhost 8086; do
  echo "influxdb daemon not running at 8086.. retrying after 3 sec"
  sleep 3
done

influx -execute 'drop database sawtooth_metrics'
influx -execute 'create database sawtooth_metrics'

wait