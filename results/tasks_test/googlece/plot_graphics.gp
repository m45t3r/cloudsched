set encoding utf8

set title "32 moldable tasks (1024x1024 matrix multiplication)"

set xlabel "Number of VMs"
set ylabel "Execution time (s)"

set xrange [0:33]
set yrange [0:400]

#set yrange [8:400]
#set logscale y

set xtics 0,2,32
set style data histogram
set boxwidth 0.75
set style fill solid
set datafile missing "-"
set datafile separator ","

# PDF output
# set term postscript enhanced color
set term pdfcairo # better quality

# PNG output
# set term pngcairo

set output "summary.pdf"
plot "summary.csv" using 1:2 title "Google CE" with boxes lc rgb 'blue', "summary.csv" using 1:2:3 notitle with yerrorbars lc rgb 'black' pt 1 lw 2
