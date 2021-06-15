window.START = false //Controls if graphs should be updating or not
window.RECORDING = "false" //Controls wether data is stored or not
window.DISCONNECTED = "true"
let UPDATE_RATIO = 1 //controls display speed. Should be between 1 and 20. 1 is max speed, 20 is min speed.
const MAX_GRAPH_SIZE = 120 //maximum number of concurrent samples per graph
const REQUEST_PERIOD = 50 //Period in ms. Every 50ms a sample is stored in the data.csv
//Graphs Initial Configuration

// Forces and Torques Graph
let initForcesGraph = () => {
    let data = [
        {
            y: [],
            type: 'scatter',
            name: 'Fz',
            line: {
                color: '#06D6A0',
                width: 3
            }
        }

    ]
    let layout = {
        title: 'Forces and Torques',
        width: 0.46 * window.innerWidth,
        height: 0.8 * window.innerHeight,
        xaxis: {
            title: {
              text: 'Samples',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            },
          },
          yaxis: {
            title: {
              text: 'Forces (N) and Torques (Nm)',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            }
          }
    }

    let config = {
        responsive: true
    }

    Plotly.newPlot('graph1', data, layout, config)
}

// Positions Graph
let initPositionGraph = () => {
    let data = [
        {
            y: [],
            type: 'scatter',
            name: 'Ax',
            line: {
                color: '#EF476F',
                width: 5
            }
        },
        {
            y: [],
            type: 'scatter',
            name: 'Ay',
            line: {
                color: '#FFD166'
            }
        },
        {
            y: [],
            type: 'scatter',
            name: 'Az',
            line: {
                color: '#118AB2'
            }
        },

    ]
    let layout = {
        title: 'Positions',
        width: 0.5 * window.innerWidth,
        height: 0.8 * window.innerHeight,
        xaxis: {
            title: {
              text: 'Samples',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            },
          },
          yaxis: {
            title: {
              text: 'Positions (m)',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            }
          }
    }

    let config = {
        responsive: true
    }

    Plotly.newPlot('graph2', data, layout, config)
}

// Positions Forces and Torques Graph
let initMixedGraph = () => {
    let data = [
        

        {
            y: [],
            type: 'scatter',
            name: 'Fz',
            line: {
                color: '#06D6A0',
            }
        },
        {
            y: [],
            type: 'scatter',
            name: 'Ax',
            line: {
                color: '#EF476F'
            }
        },
        {
            y: [],
            type: 'scatter',
            name: 'Ay',
            line: {
                color: '#FFD166'
            }
        },
        {
            y: [],
            type: 'scatter',
            name: 'Az',
            line: {
                color: '#118AB2'
            }
        },

    ]
    let layout = {
        title: 'Positions, Forces and Torques',
        width: 0.8 * window.innerWidth,
        height: 0.8 * window.innerHeight,
        xaxis: {
            title: {
              text: 'Samples',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            },
          },
          yaxis: {
            title: {
              text: 'Positions (m), Forces (N) and Torques (Nm)',
              font: {
                size: 14,
                color: '#7f7f7f'
              }
            }
          }
    }

    let config = {
        responsive: true
    }

    Plotly.newPlot('graph3', data, layout, config)
}

// Utility function to format data in a plotly.js friendly way
// rawData = [fx, fy, fz, tx, ty, tz]
let formatData = (rawData) => {
    let formatedData = []
    rawData.forEach(element => {
        formatedData.push([element])
    });
    
    return formatedData
}


let countMod = 0;

//Update graph data and axis function
setInterval(function(){
    if(window.START) {
        
        readNetBoxSamples().then((samples) => {
            
            //let data = formatData([samples.fx, samples.fy, samples.fz, samples.tx, samples.ty, samples.tz])
            let posData = formatData([samples.ax, samples.ay, samples.az])
            //let allData = formatData([samples.fx, samples.fy, samples.fz, samples.tx, samples.ty, samples.tz, samples.ax, samples.ay, samples.az, samples.aw])
            let allData = formatData([samples.fz, samples.ax, samples.ay, samples.az])
            Plotly.extendTraces('graph1', {y: [[samples.fz]]}, [0])
            Plotly.extendTraces('graph2', {y: posData}, [0, 1, 2])
            Plotly.extendTraces('graph3', {y: allData}, [0, 1, 2, 3])
            countMod += 1
            document.getElementById("values").innerHTML = `
            <div class="bg pink"><b>Ax:</b> ${samples.ax.toFixed(3)} mm</div> 
            <div class="bg yellow"><b>Ay:</b> ${samples.ay.toFixed(3)} mm</div> 
            <div class="bg blue"><b>Az:</b> ${samples.az.toFixed(3)} mm</div> 
            <div class="bg green"><b>Fz:</b> ${samples.fz.toFixed(3)} N</div>`
            if (countMod > MAX_GRAPH_SIZE){
                Plotly.relayout('graph1', {
                    xaxis: {
                        range: [countMod-MAX_GRAPH_SIZE, countMod]
                    }
                })
                Plotly.relayout('graph2', {
                    xaxis: {
                        range: [countMod-MAX_GRAPH_SIZE, countMod]
                    }
                })
                Plotly.relayout('graph3', {
                    xaxis: {
                        range: [countMod-MAX_GRAPH_SIZE, countMod]
                    }
                })
            }
        })
    }
}, 300)


async function readNetBoxSamples () {
    let res = await fetch('http://127.0.0.1:4000/api/readsamples?' + new URLSearchParams({
        write: window.RECORDING
    }), {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json',
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      })
    let toReturn = await res.json()
    return toReturn
}

async function connect() {
    let res = await fetch('http://127.0.0.1:4000/api/connect', {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json',
          // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      })
    let toReturn = await res.json()
    return toReturn
}

async function disconnect() {
    let res = await fetch('http://127.0.0.1:4000/api/disconnect' , {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache', 
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json',
        },
        redirect: 'follow', 
        referrerPolicy: 'no-referrer', 
      })
    let toReturn = await res.json()
    return toReturn
}

async function tareClipx() {
    let res = await fetch('http://127.0.0.1:4000/api/tareloadcell' , {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache', 
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json',
        },
        redirect: 'follow', 
        referrerPolicy: 'no-referrer', 
      })
    let toReturn = await res.json()
    return toReturn
}

async function tareHeiden() {
    let res = await fetch('http://127.0.0.1:4000/api/tareheiden' , {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache', 
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json',
        },
        redirect: 'follow', 
        referrerPolicy: 'no-referrer', 
      })
    let toReturn = await res.json()
    return toReturn
}
/*

 <------- Buttons functionalities -------->

 */

document.getElementById("start-btn").addEventListener("click", (e) => {
    if(window.DISCONNECTED){
        window.alert("You can not start because you are disconnected. Please click connect before start")
    }else{
        
        window.START = true
    }
   
})

document.getElementById("stop-btn").addEventListener("click", (e) => window.START = false)
document.getElementById("connect-btn").addEventListener("click", (e) => {
    connect().then((res) => {
        let msg = `[SERVER MESSAGE]: ${res.message}\nData would be stored at ${res.filename}`
        localStorage.setItem("filename", res.filename)
        window.alert(msg)
        if(res.message == "Connection sucessful") {
            console.log("response is okay")
            window.DISCONNECTED = false
        } 
    })
})

document.getElementById("isRecording").addEventListener("change", (e) => {
    document.getElementById("isRecording").checked ? window.RECORDING = "true" : window.RECORDING ="false"
})

document.getElementById("disconnect-btn").addEventListener("click", (e) => {
    let confirm = window.confirm("¿Are you sure that you want to disconnect?")
    if(confirm) {
        window.DISCONNECTED = true
        window.START = false
        disconnect().then((response) => {
            window.alert(response.message)
        })
    }
})

document.getElementById("tare-clipx").addEventListener("click", (e) => {
    tareClipx().then((res) => {
        let msg = `[SERVER MESSAGE]: ${res.message}`
        window.alert(msg)
    })
})

document.getElementById("tare-heiden").addEventListener("click", (e) => {
    tareHeiden().then((res) => {
        let msg = `[SERVER MESSAGE]: ${res.message}`
        window.alert(msg)
    })
})


/*

 <------- Style and Responsiveness functions -------->

 */

//Relayout function
window.onresize = function() {
    Plotly.relayout('graph1', {
      width: 0.46 * window.innerWidth,
      height: 0.8 * window.innerHeight
    })
    Plotly.relayout('graph2', {
        width: 0.46 * window.innerWidth,
        height: 0.8 * window.innerHeight
      })
    Plotly.relayout('graph3', {
    width: 0.8 * window.innerWidth,
    height: 0.8 * window.innerHeight
    })  
  }

//Change graphs order  
let changeView = () => {
    document.getElementById("change-view-btn").addEventListener("click", (e) => {
        let wrapper = document.getElementById("graphs")
        console.log( document.getElementById("graphs").style.flexDirection)
        wrapper.style.flexDirection == "" 
        ? wrapper.style.flexDirection = "column-reverse" 
        : wrapper.style.flexDirection == "column-reverse"
        ? wrapper.style.flexDirection = "column"
        : wrapper.style.flexDirection = "column-reverse"
    })
    
}

/*

 <------- Main Execution -------->
 
 */
initForcesGraph();
initPositionGraph();
initMixedGraph();
changeView();


