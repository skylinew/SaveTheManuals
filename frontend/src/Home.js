import React from 'react';

const FETCH_URL = 'http://localhost:4000/cars'


class Home extends React.Component {
    
    constructor(props){
        super(props);
        this.state = {
            cars_list: []

        }
    }

    componentWillMount(){
        
        let options = {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            }
        }

        fetch(FETCH_URL, options)
            .then((res)=>{
           
                if (res.status !== 200){
                    console.log('Error retrieving cars list from server: 200');
                }
                else{
                    return res.json();
                }
                
            })
            .then((data)=>{
                console.log(data.cars);
              
                this.setState({cars_list: data.cars});
            });
            
        

           
    }




    render(){

        const listElement = this.state.cars_list.map((car)=>{
            return(
                                <li className="list_item"
                                    key={car.Make + '~' + car.model}>
                                    <div className="make">{car.make}</div>
                                    <div className="model">{car.model}</div>
                                </li>
        )})
                            
                            
        let plural = this.state.cars_list.length === 1 ? 'Car' : 'Cars';

        return (


            
            <div>
                
                
                <div className="image">
                    <div className="top_wrapper">
                        <div className="number">{this.state.cars_list.length}</div>
                        <div className="title">{plural} Remaining with Manual Transmission in the U.S.</div>
                    </div>
                </div>
                   
                <ol className="list">
                  
                        {listElement}
                   
                </ol>
        

                <div className="footer">
        
                    Photo Source: 
                    <br/>
                    https://pixabay.com/users/stocksnap-894430/

                    <br/>
                    <br/>

                    Powered By:
                    <br/>   
                    BS4, Requests/HTML-Requests

                    <br/>
                    <br/>
                    Email Feedback/Errors:
                    <br/>
                     savethestickshifts.gmail.com
                
                </div>



            </div> 
        )
    }

}

export default Home;