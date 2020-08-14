/**
 * Global variables
 */
// table
var table;

$(document).ready(function ()
{
    // activate datatable
    table = $('#crossing-probabilities').DataTable(
    {
        "scrollX": true,
        lengthMenu: [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"]],
        "order": [[ 1, 'desc' ]]
    });

    // Plotly doc:
    // https://plotly.com/javascript/reference/
    var data = [
      {
        x: labels,
        y: rows,
        z: matrix,
        type: 'heatmap',
        hoverongaps: false
      }
    ];

    var layout = {
        title: 'Projection matrix',
        //margin: {t:0,r:0,b:0,l:20},
        automargin: true,
        xaxis: {
            categoryorder: "category ascending",
            automargin: true,
            tickangle: 0,
            title: {
                text: "Structures",
                standoff: 20
            }
        },
        yaxis: {
            type: "category",
            automargin: true,
            tickangle: 0,
            title: {
                text: "Experiments",
                standoff: 40
            }
        }
    };

    Plotly.newPlot('matrix-div', data, layout);
});

// https://plotly.com/javascript/heatmaps/