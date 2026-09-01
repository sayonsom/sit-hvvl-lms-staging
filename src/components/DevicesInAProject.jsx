import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid'
import ListOfAvailableDevicesInAProject from './ListOfAvailableDevicesInAProject'

export default function DevicesInAProject() {
    return (
        <>
         <div className="min-h-full">   
            <div className="mx-auto w-full max-w-7xl px-6 pb-16 pt-10 sm:pb-24 lg:px-8">
            <div>
        <nav className="sm:hidden" aria-label="Back">
          <a href="#" className="flex items-center text-sm font-medium text-gray-500 hover:text-gray-700">
            <ChevronLeftIcon className="-ml-1 mr-1 h-5 w-5 flex-shrink-0 text-gray-400" aria-hidden="true" />
            Back
          </a>
        </nav>
        <nav className="hidden sm:flex" aria-label="Breadcrumb">
          <ol role="list" className="flex items-center space-x-4">
            <li>
              <div className="flex">
                <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-700 font-sans dark:text-gray-400">
                  My Projects
                </a>
              </div>
            </li>
            <li>
              <div className="flex items-center">
                <ChevronRightIcon className="h-5 w-5 flex-shrink-0 text-gray-400" aria-hidden="true" />
                <a href="#" className="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700 font-sans dark:text-gray-400">
                  "Project Name"
                </a>
              </div>
            </li>
            <li>
              <div className="flex items-center">
                <ChevronRightIcon className="h-5 w-5 flex-shrink-0 text-gray-400" aria-hidden="true" />
                <a href="#" aria-current="page" className="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700 font-sans dark:text-gray-400">
                  Devices
                </a>
              </div>
            </li>
          </ol>
        </nav>
            </div>
            {/* PROJECT PAGE HEADER */}
            <div className="mt-2 md:flex md:items-center md:justify-between">
                <div className="min-w-0 flex-1">
                <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight font-heading dark:text-white">
                    Devices Used
                </h2>
                </div>
                <div className="mt-4 flex flex-shrink-0 md:ml-4 md:mt-0">
                {/* <button
                    type="button"
                    className="font-sans inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                    Edit
                </button>
                <button
                    type="button"
                    className="font-sans ml-3 inline-flex items-center rounded-md bg-black px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                >
                    Deploy
                </button> */}
                </div>
            </div>
            {/* LIST OF DEVICES */}
            <ListOfAvailableDevicesInAProject />
            </div>
            </div>
             
        </>
    )
}