#!/usr/bin/gnuplot

set encoding utf8

#set title "32 moldable tasks (1024x1024 matrix multiplication)"

set xlabel "Number of VMs"
set ylabel "Execution time (s)"

set xrange [0:33]

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

set output "summary_azure.pdf"
set yrange [0:600]
plot azure using 1:2 title "Expected Time" with lines, azure using 1:3 title "Measured Time" with lines, azure using 1:3:4 notitle with yerrorbars lc rgb 'black' pt 1 lw 2

set yrange [0:450]
set output "summary_googlece.pdf"
plot googlece using 1:2 title "Expected Time" with lines, googlece using 1:3 title "Measured Time" with lines, googlece using 1:3:4 notitle with yerrorbars lc rgb 'black' pt 1 lw 2
