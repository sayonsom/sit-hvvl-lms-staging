import { useState } from 'react';
import axios from 'axios';

import { Button } from './button'
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from './dialog'
import { Description, Field, FieldGroup, Fieldset, Label, Legend } from './fieldset'
import { Input } from './input'
import { Select } from './select'
import { Text } from './text'
import { Textarea } from './textarea'


function NewProjectCreation() {
  let [isOpen, setIsOpen] = useState(false);
  let [projectName, setProjectName] = useState('');
  let [projectDescription, setProjectDescription] = useState('');
  let [selectedDevices, setSelectedDevices] = useState([]);

  const handleCreateProject = async () => {
    setIsOpen(false);

    // Construct the payload
    const payload = {
      projectName,
      projectDescription,
      devices: selectedDevices,
    };

    try {
        console.log(payload)
      const response = await axios.post('YOUR_API_ENDPOINT', payload);
      // Handle the response here
      console.log(response);
    } catch (error) {
      // Handle the error here
      console.error(error);
    }
  };

  return (
    <>
      <Button type="button" onClick={() => setIsOpen(true)}>
        Take a New Course
      </Button>
      <Dialog open={isOpen} onClose={setIsOpen} size="xl">
        <DialogTitle>Select from the available new courses</DialogTitle>
        {/* <DialogDescription>All fields are necessary to create a project</DialogDescription> */}
        {/* <DialogBody className="text-sm/6 text-zinc-900 dark:text-white">
          <form onSubmit={(e) => e.preventDefault()}>
            <Fieldset>
              <FieldGroup>
                <Field>
                  <Label>Project Name</Label>
                  <Input name="project_name" onChange={(e) => setProjectName(e.target.value)} />
                </Field>
                <Field>
                  <Label>Project Description</Label>
                  <Textarea name="notes" onChange={(e) => setProjectDescription(e.target.value)} />
                </Field>
                <Field>
                  <Label>Grid Edge Devices</Label>
                  {/* Pass setSelectedDevices to the ListOfAvailableDevices component */}
                  {/* <ListOfAvailableDevices setSelectedDevices={setSelectedDevices} />
                </Field>
              </FieldGroup>
            </Fieldset>
          </form>
        </DialogBody> */} 
        <DialogActions>
          <Button plain onClick={() => setIsOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateProject}>Enroll</Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default NewProjectCreation;
