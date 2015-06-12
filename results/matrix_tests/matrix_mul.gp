set encoding utf8

set title "32 moldable tasks (1024x1024 matrix multiplication)"

set xlabel "Number of VMs"
set ylabel "Execution time (s)"

#set style line 1 lw 3
#set style line 2 lw 3
#set style line 3 lw 3
#set style line 4 lw 3
#set style line 5 lw 3
#set style line 6 lw 3
#set style line 7 lw 3
#set style line 8 lw 3
set xrange [0:33]
set yrange [0:400]
#set yrange [8:400]

set xtics 0,2,32
set style data histogram
set boxwidth 0.75
set style fill solid
#set style histogram cluster gap 1
#set datafile missing "-"

#set logscale y

set datafile separator ","

# PDF output
# set term postscript enhanced color
set term pdfcairo # better quality

# PNG output
# set term pngcairo

set output "results.pdf"
plot "results.csv" using 1:2 title "Google CE" with boxes ls 2, "results.csv" using 1:2:3 notitle with yerrorbars lc rgb 'black' pt 1 lw 2
#plot "results.csv" using 1:2 title "Google CE" with lines ls 2, "results.csv" using 1:2:3 notitle with yerrorbars lc rgb 'black' pt 1 lw 2
