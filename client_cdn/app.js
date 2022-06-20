    




const app = Vue.createApp({
    
    el : 'iadd',               
    data(){
        return {
            firstName: '',
            info: null,
            itemname: null,
            itemamount: null, 
            itemname_u: null,
            itemamount_u: null, 
            file: null,                       
            message: null,
            key: null
        }
    },
    async mounted () {                
        await axios
        .get('http://localhost:8080/budget')
        .then(response => (this.info = response.data)
        )

        this.info.sort((a, b) => {
            return a.description.localeCompare(b.description);
        });    
    },
    methods : {          
        async postItem(){              

            await axios.post('http://localhost:8080/budget', { description: this.itemname,
                                                         amount: this.itemamount})
            .then(res => {
                // do something with res
            })
            .catch(err => {});

            /*
            axois.post('http://localhost:8080/budget', {
            description: this.itemname,
            amount: this.itemamount
            })
            .then(function(response){
                console.log(response);
            })
            .catch(function(error){
                console.log(error);
            })
            */
            
          },
    
          async deleteItem(id){                                      
            await axios.delete(`http://localhost:8080/budget/${id}`, )
            .then(res => {
                // do something with res
                axios
                .get('http://localhost:8080/budget')
                .then(response => (this.info = response.data)
                )                
            })
            .catch(err => {});
            
            
            
          },

          async updateItem(id){  
            //console.log(this.itemamount)
            
            console.log(id)
            await axios.put(`http://localhost:8080/budget/${id}`, { description: this.itemname_u,
                                                              amount: this.itemamount_u} )
            .then(res => {
                // do something with res
                
                axios
                .get('http://localhost:8080/budget')
                .then(response => (this.info = response.data)
                )
                
            })
            .catch(err => {});
            
            
            
            
            
          },

          showModal(id){  
            console.log(id)
            modalname = '#updatemodal' + id
            console.log(modalname)
            axios.get(`http://localhost:8080/budget/${id}`, )
            .then(res => {
                // do something with res
                this.key = res.data[0].id
                this.itemamount_u = res.data[0].amount
                this.itemname_u = res.data[0].description
                console.log(res.data[0].amount)
            })
            .catch(err => {});
            // $(modalname).modal('show')
            $(modalname).modal('toggle')
 
          },

          hideModal(id){  
            modalname = '#updatemodal' + id
            console.log(modalname)           
            $(modalname).modal('toggle')
            
 
          },

          uploadExpenses(event){
            
            var input = event.target;
            var reader = new FileReader();
            reader.onload = () => {
              var fileData = reader.result;
              console.log(fileData);
              var wb = XLSX.read(fileData, {type : 'binary'});
              wb.SheetNames.forEach((sheetName) => {
                  var rowObj =XLSX.utils.sheet_to_json(wb.Sheets[sheetName]);	        
                this.excelData = JSON.stringify(rowObj)
              })
            };
            reader.readAsBinaryString(input.files[0]);
          }
           
            
          

    }
})  


app.mount('#app')