import React, { useEffect, useState } from "react";
import SidebarComponent from "../components/SidebarComponent";
import { ChevronRightIcon } from '@heroicons/react/20/solid'
import { BookmarkSquareIcon, BookOpenIcon, QueueListIcon, RssIcon } from '@heroicons/react/24/solid'
import AdBanner from "../components/AdBanner";
import AppLayout from "./AppLayout";


// This function is called after successfully creating a user with ClerkJS


export default function NotInDemo() {
  

    const links = [
        {
          name: 'Get a personal demo',
          href: 'https://plexflo.com/try',
          description: 'Fill out this form and we’ll be in touch.',
          icon: BookOpenIcon,
        },
        { name: 'API Reference', href: 'https://sofiabackendapi.azurewebsites.net/', description: 'A complete API reference for our libraries.', icon: QueueListIcon },
        {
          name: 'Guides',
          href: 'mailto:support@plexflo.com',
          description: 'We typically ship a PDF Documentation with your purchase. If you need a PDF guide help just email us.',
          icon: BookmarkSquareIcon,
        },
        { name: 'Blog', href: '#', description: 'Read our latest blog about power outages', icon: RssIcon },
      ]
  


  
    return (
        <>
        <AppLayout>
        <div>
            <div className="min-h-full">   
            <div className="mx-auto w-full max-w-7xl px-6 pb-16 pt-10 sm:pb-24 lg:px-8 font-sans">
        <img
          className="mx-auto h-20 w-auto sm:h-20"
          src="https://res.cloudinary.com/dti7egpsg/image/upload/v1692052277/evidence_logo_final_2_kp7lmk.png"
          alt="SOFIA Logo"
        />
        <div className="mx-auto mt-20 max-w-2xl text-center sm:mt-24">
          <p className="text-base font-semibold leading-8 text-red-600">Not in Demo</p>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-gray-900 sm:text-5xl font-heading">This feature is disabled</h1>
          <p className="mt-4 text-base leading-7 text-gray-600 sm:mt-6 sm:text-lg sm:leading-8">
            Please book a full, personalized demo to see this feature in action
          </p>
        </div>
        <div className="mx-auto mt-16 flow-root max-w-lg sm:mt-20">
          <h2 className="sr-only">Your options</h2>
          <ul role="list" className="-mt-6 divide-y divide-gray-900/5 border-b border-gray-900/5">
            {links.map((link, linkIdx) => (
              <li key={linkIdx} className="relative flex gap-x-6 py-6">
                <div className="flex h-10 w-10 flex-none items-center justify-center rounded-lg shadow-sm ring-1 ring-gray-900/10">
                  <link.icon className="h-6 w-6 text-red-600" aria-hidden="true" />
                </div>
                <div className="flex-auto">
                  <h3 className="text-sm font-semibold leading-6 text-gray-900 font-heading">
                    <a href={link.href}>
                      <span className="absolute inset-0" aria-hidden="true" />
                      {link.name}
                    </a>
                  </h3>
                  <p className="mt-2 text-sm leading-6 text-gray-600">{link.description}</p>
                </div>
                <div className="flex-none self-center">
                  <ChevronRightIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-10 flex justify-center">
            <a href="" className="text-sm font-semibold leading-6 text-red-600">
              <span aria-hidden="true">&larr;</span>
              Back to home
            </a>
            {/* Navigate back to react home page */}

          </div>
        </div>
            </div>
            </div>
          </div>

        </AppLayout>

          
          
          


        </>
        
      );
}