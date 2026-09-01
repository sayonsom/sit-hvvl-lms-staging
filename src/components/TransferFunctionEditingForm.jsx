import { useState } from 'react';
import axios from 'axios';

import { PhotoIcon, UserCircleIcon, CodeBracketIcon } from '@heroicons/react/24/solid'
import InfoIcon from './InfoIcon'
import ListenChannels from './ListenChannels'
import ListOfAvailableDevices from './ListOfAvailableDevices'


export default function TransferFunctionEditingForm( { tfName }) {
    let [selectedDevices, setSelectedDevices] = useState([]);
    return (
        <>
            <form className='font-sans'>
                <div className="space-y-12 ">
                    <div className="">
                    
                    <h2 className="pt-4 text-base font-semibold leading-7 text-gray-900">Step 1: Basics</h2>
                        <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                            <div className="sm:col-span-4 ">
                            <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
                                Transfer Function Name
                            </label>
                                <div className="mt-2">
                                        <div className="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-red-600 sm:max-w-md">
                                        <span className="flex select-none items-center pl-3 text-gray-500 sm:text-sm">evidenceapp.com/nrel.gov/</span>
                                        <input
                                            type="text"
                                            name="username"
                                            id="username"
                                            autoComplete="username"
                                            className="block flex-1 border-0 bg-transparent py-1.5 pl-1 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
                                            placeholder={ tfName }
                                        />
                                        </div>
                                </div>
                            </div>

                            <div className="col-span-full">
                            <label htmlFor="about" className="block text-sm font-medium leading-6 text-gray-900">
                                Description
                            </label>
                            <div className="mt-2">
                                <textarea
                                id="about"
                                name="about"
                                rows={3}
                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                defaultValue={''}
                                />
                            </div>
                            <p className="mt-3 text-sm leading-6 text-gray-600">Please write a short note so that other users can understand the specifics of what has been modeled and deployed</p>
                            </div>


                            <div className="col-span-full">
                                <label htmlFor="cover-photo" className="block text-sm font-medium leading-6 text-gray-900">
                                    Python Model
                                </label>
                                <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-6">
                                    <div className="sm:col-span-3">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0">
                                                <div className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
                                                    <div className="text-center">
                                                        <CodeBracketIcon className="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
                                                        <div className="mt-4 flex text-sm leading-6 text-gray-600">
                                                            <label
                                                                htmlFor="file-upload"
                                                                className="relative cursor-pointer rounded-md bg-white font-semibold text-red-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-red-600 focus-within:ring-offset-2 hover:text-red-500"
                                                            >
                                                                <span>Upload a *.py file</span>
                                                                <input id="file-upload" name="file-upload" type="file" className="sr-only" />
                                                            </label>
                                                            <p className="pl-1">or drag and drop</p>
                                                        </div>
                                                        <p className="text-xs leading-5 text-gray-600">Validated, single *.py file up to 10MB</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    {/* Corrected closing tag for the div */}
                                </div>


                                <div className="border-b border-gray-900/10 pb-12 pt-12">
                                <h2 className="text-base font-bold leading-7 text-gray-900">Step 2: Transfer Function Settings</h2>
                                <p className="mt-1 pt-4 text-sm font-semibold leading-6 text-gray-600">Value1  <InfoIcon docUrl="https://docs.evidenceapp.com/transfer-functions/transfer-function-settings" /> </p>
                                


                                <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                                    <div className="sm:col-span-3">
                                        <div className="relative">
                                            <label
                                                htmlFor="value1_name"
                                                className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                            >
                                                Name
                                            </label>
                                            <input
                                                type="text"
                                                name="value1_name"
                                                id="value1_name"
                                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                placeholder="TF Name"
                                            />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-3">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value1_units"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Initial Value
                                                </label>
                                                <input
                                                    type="text"
                                                    name="value1_units"
                                                    id="value1_units"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="Percentage"
                                                />
                                        </div>
                                    </div>

                                    
                                    </div>

                                    <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-8">
                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                            <label
                                                htmlFor="value1_defaultValue"
                                                className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                            >
                                                Default Value
                                            </label>
                                            <input
                                                type="number"
                                                name="value1_defaultValue"
                                                id="value1_defaultValue"
                                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                placeholder="0.0"
                                            />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value1_initialValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Initial Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value1_initialValue"
                                                    id="value1_initialValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="51.67"
                                                />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value1_maxValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Max Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value1_maxValue"
                                                    id="value1_maxValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="100"
                                                />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value1_minValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Min Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value1_minValue"
                                                    id="value1_minValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="0"
                                                />
                                        </div>
                                    </div>
                                    </div>

                                    <div className="sm:col-span-2 sm:col-start-1">

                                    <div className="mt-2">
                                    <fieldset>
                                    <div className="mt-6 space-y-6">
                                        <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input
                                            id="comments"
                                            name="comments"
                                            type="checkbox"
                                            className="h-4 w-4 rounded border-gray-300 text-red-600 focus:ring-red-600"
                                            />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="comments" className="font-medium text-gray-900">
                                            Stateful
                                            </label>
                                            <p className="text-gray-500">The last value of this signal in this database will be used to calculate the next step</p>
                                        </div>
                                        </div>
                                        <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input
                                            id="candidates"
                                            name="candidates"
                                            type="checkbox"
                                            className="h-4 w-4 rounded border-gray-300 text-red-600 focus:ring-red-600"
                                            />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="candidates" className="font-medium text-gray-900">
                                            Reset at next deploy
                                            </label>
                                            <p className="text-gray-500">Set to initial value given in this form, when the transfer function is deployed again on the edge devices/controllers</p>
                                        </div>
                                        </div>
                                    </div>
                                    </fieldset>
                                    </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <ListenChannels />
                                    </div>


                                    <p className="mt-1 pt-4 text-sm font-semibold leading-6 text-gray-600">value2  <InfoIcon docUrl="https://docs.evidenceapp.com/transfer-functions/transfer-function-settings" /> </p>
                                


                                <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                                    <div className="sm:col-span-3">
                                        <div className="relative">
                                            <label
                                                htmlFor="value2_name"
                                                className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                            >
                                                Name
                                            </label>
                                            <input
                                                type="text"
                                                name="value2_name"
                                                id="value2_name"
                                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                placeholder="TF Name"
                                            />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-3">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value2_units"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Initial Value
                                                </label>
                                                <input
                                                    type="text"
                                                    name="value2_units"
                                                    id="value2_units"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="Percentage"
                                                />
                                        </div>
                                    </div>

                                    
                                    </div>

                                    <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-8">
                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                            <label
                                                htmlFor="value2_defaultValue"
                                                className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                            >
                                                Default Value
                                            </label>
                                            <input
                                                type="number"
                                                name="value2_defaultValue"
                                                id="value2_defaultValue"
                                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                placeholder="0.0"
                                            />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value2_initialValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Initial Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value2_initialValue"
                                                    id="value2_initialValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="51.67"
                                                />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value2_maxValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Max Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value2_maxValue"
                                                    id="value2_maxValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="100"
                                                />
                                        </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <div className="relative">
                                                <label
                                                    htmlFor="value2_minValue"
                                                    className="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900"
                                                >
                                                    Min Value
                                                </label>
                                                <input
                                                    type="number"
                                                    name="value2_minValue"
                                                    id="value2_minValue"
                                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
                                                    placeholder="0"
                                                />
                                        </div>
                                    </div>
                                    </div>

                                    <div className="sm:col-span-2 sm:col-start-1">

                                    <div className="mt-2">
                                    <fieldset>
                                    <div className="mt-6 space-y-6">
                                        <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input
                                            id="comments"
                                            name="comments"
                                            type="checkbox"
                                            className="h-4 w-4 rounded border-gray-300 text-red-600 focus:ring-red-600"
                                            />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="comments" className="font-medium text-gray-900">
                                            Stateful
                                            </label>
                                            <p className="text-gray-500">The last value of this signal in this database will be used to calculate the next step</p>
                                        </div>
                                        </div>
                                        <div className="relative flex gap-x-3">
                                        <div className="flex h-6 items-center">
                                            <input
                                            id="candidates"
                                            name="candidates"
                                            type="checkbox"
                                            className="h-4 w-4 rounded border-gray-300 text-red-600 focus:ring-red-600"
                                            />
                                        </div>
                                        <div className="text-sm leading-6">
                                            <label htmlFor="candidates" className="font-medium text-gray-900">
                                            Reset at next deploy
                                            </label>
                                            <p className="text-gray-500">Set to initial value given in this form, when the transfer function is deployed again on the edge devices/controllers</p>
                                        </div>
                                        </div>
                                    </div>
                                    </fieldset>
                                    </div>
                                    </div>

                                    <div className="sm:col-span-2">
                                        <ListenChannels />
                                    </div>


                                </div>

                                <div className="border-b border-gray-900/10 pt-6 pb-6">
                        <h2 className="text-base font-semibold leading-7 text-gray-900">Step 3: Devices to deploy on</h2>
                        <p className="mt-1 text-sm leading-6 text-gray-600">
                            Review documentation for list of supported OS and minimum requirements. 
                        </p>

                        <div className="mt-10 space-y-10">
                            <fieldset>

                            <div key='optionToDeployDevice' className="relative flex items-start">
                                <div className="flex h-6 items-center">
                                <input
                                    id='optionToDeployDevice'
                                    aria-describedby='optionToDeployDevice'
                                    name="plan"
                                    type="radio"
                                    className="h-4 w-4 border-gray-300 text-red-600 focus:ring-red-600"
                                />
                                </div>
                                
                                <div className="ml-3 text-sm leading-6 col-span-full">
                                    <label htmlFor="ipAddressBank" className="font-medium text-gray-900">
                                        Option 1: By IP Address Banks
                                        </label>

                                        <div className="mt-2 grid grid-cols-1 gap-y-8 col-span-full">
                                            <div className="col-span-full">
                                            
      <div className="mt-2 col-span-full">
        <input
          type="email"
          name="email"
          id="email"
          className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6"
          placeholder="['10.77.1.10', '10.77.1.11'] OR ['10.77.1.10', '10.77.1.11']"
        />
      </div>
                                            </div>



                        
                        </div>
                                        
                                </div>

                                
                                
                            </div>
                            <div key='optionToDeployDevice2' className="relative flex items-start pt-6">
                                <div className="flex h-6 items-center ">
                                <input
                                    id='optionToDeployDevice'
                                    aria-describedby='optionToDeployDevice'
                                    name="plan"
                                    type="radio"
                                    className="h-4 w-4 border-gray-300 text-red-600 focus:ring-red-600"
                                />
                                </div>
                                
                                <div className="ml-3 text-sm leading-6">
                                    <label htmlFor="{plan.id}" className="font-medium text-gray-900">
                                        Option 2: Select device(s) from list
                                        </label>
                                        <ListOfAvailableDevices setSelectedDevices={setSelectedDevices} />
                                </div>

                                
                                
                            </div>
                            
                            </fieldset>
                            
                        </div>
                        </div>
                            </div>

                        
                        </div>

                        <div className="mt-6 flex items-center justify-end gap-x-6">

                        <div className="mt-4 flex flex-shrink-0 md:ml-4 md:mt-0">
                        <button
                            type="button"
                            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-sans font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                        >
                            Delete
                        </button>
                        <button
                            type="button"
                            className="ml-3 inline-flex items-center rounded-md bg-black px-3 py-2 text-sm font-sans font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                        >
                            Deploy
                        </button>
                        </div>
                        </div>
                        </div>
                        </div>
            </form>
        </>
    )
                
}