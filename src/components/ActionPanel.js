import React, { useState } from 'react';
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from '../components/dialog';
import { Strong, Text, TextLink } from '../components/text'
import { Dropdown, DropdownButton, DropdownItem, DropdownMenu } from '../components/dropdown';
import { Button } from '../components/button';
import { ChevronDownIcon } from '@heroicons/react/16/solid'

const ActionPanel = () => {
    const [isOpen, setIsOpen] = useState(false);

    const togglePanel = () => {
        setIsOpen(!isOpen);
    };

    return (
        <>
 <div className="fixed bottom-0 right-0 m-4">
 <Dropdown>
        <DropdownButton>
          Action Options
          <ChevronDownIcon />
        </DropdownButton>
        <DropdownMenu>
          <DropdownItem onClick={() => setIsOpen(true)}>Create new work order</DropdownItem>
          <DropdownItem href="#" disabled>
            Action History
          </DropdownItem>
        </DropdownMenu>
      </Dropdown>
 </div>


            <Dialog open={isOpen} onClose={setIsOpen}>
                <DialogTitle>Create a Work Order</DialogTitle>
                <DialogDescription>
                All the conversations and discussions related to work orders related to today's outage can be coordinated here.
                </DialogDescription>
                <DialogBody>
                <Text>
                    Do you want to create a new work order?
                </Text>
                </DialogBody>
                <DialogActions>
                <Button plain onClick={() => setIsOpen(false)}>
                    Cancel
                </Button>
                <Button onClick={() => setIsOpen(false)}>Place Order</Button>
                </DialogActions>
            </Dialog>

        </>
            

            

    );
};

export default ActionPanel;
