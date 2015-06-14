#!/usr/bin/gnuplot

set encoding utf8

set title "32 moldable tasks (1024x1024 matrix multiplication)"

set xlabel "Number of VMs"
set ylabel "Execution time (s)"

set xrange [0:33]
set yrange [0:500]

#set yrange [8:500]
#set logscale y

set xtics 0,2,32
set terminal pdfcairo linewidth 1
set terminal pngcairo linewidth 1
set datafile missing "-"
set datafile separator ","

# PDF output
# set term postscript enhanced color
set term pdfcairo # better quality

# PNG output
# set term pngcairo

azure = "summary_azure.csv"
googlece = "summary_googlece.csv"

set output "summary.pdf"
plot azure using 1:2 title "Microsoft Azure" with lines lc rgb 'blue', azure using 1:2:3 notitle with yerrorbars lc rgb 'black' pt 1 lw 2, googlece using 1:2 title "Google CE" with lines lc rgb 'green', googlece using 1:2:3 notitle with yerrorbars lc rgb 'black' pt 1 lw 2
