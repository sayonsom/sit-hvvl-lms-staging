import { Fragment, useState, useEffect } from 'react'
import { Dialog, Menu, Transition } from '@headlessui/react'
import { useLTI } from "../contexts/LTIContext";
import {
  BellIcon,
  Cog6ToothIcon,
  DocumentDuplicateIcon,
  AcademicCapIcon,
  XMarkIcon,
  Bars3Icon,
  BookOpenIcon,
  PencilIcon,
  ShieldCheckIcon,
  TruckIcon,
  WrenchScrewdriverIcon,
  ChartBarIcon,
  HomeIcon,
  ServerStackIcon,
  WifiIcon,
  PhoneArrowUpRightIcon
} from '@heroicons/react/24/outline'
import { ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/react/20/solid'
import AdBanner from '../components/AdBanner'
import DarkModeToggle from '../components/DarkModeToggle'

const baseNavigation = [
  { name: 'Home', href: '/home', icon: HomeIcon, current: true },
  { name: 'My Submissions', href: '/results', icon: PencilIcon, current: false },
  { name: 'Tech Help', href: '/contact', icon: PhoneArrowUpRightIcon, current: false },
]
const teams = [
  { id: 1, name: 'Default', href: '/not-in-demo', initial: 'D', current: false }
]

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout, isAuthenticated, isLoading, authMethod } = useLTI();

  const navigation = [
    ...baseNavigation,
    ...(authMethod === 'staff' ? [
      { name: 'Student Results', href: '/manage/results', icon: ChartBarIcon, current: false },
      { name: 'Manage', href: '/home', icon: WrenchScrewdriverIcon, current: false },
    ] : []),
  ];
  const [userFullName, setUserFullName] = useState(null);
  const [userPhoto, setUserPhoto] = useState(null);

  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('LTI User:', user);
      // Use given_name + family_name if available, otherwise use full name or email
      const displayName = user.given_name 
        ? `${user.given_name} ${user.family_name}`.trim() 
        : user.name || user.email;
      
      setUserFullName(displayName);
      setUserPhoto(user.picture || "https://res.cloudinary.com/dti7egpsg/image/upload/v1695741601/SIT%20Align/SIT_logo_2_llcb1k.png");
      return;
    }
    setUserFullName(null);
    setUserPhoto(null);
  }, [isAuthenticated, user]);

  const handleLogout = async () => {
    if (window.confirm("Are you sure you want to log out?")) {
      await logout();
    }
  };

  const handleMenuClick = async (event, pageName) => {
    event.preventDefault();
    if (pageName === "Log Out") {
      await handleLogout();
      // alert("Log Out function is disabled.");
    }
  };

  const userNavigation = [
    { name: 'Your profile', href: '#' },
    { name: 'Log Out', href: '#' },
  ]

  return (
    <>
      <div>
        <Transition.Root show={sidebarOpen} as={Fragment}>
          <Dialog as="div" className="relative z-50 lg:hidden font-sans" onClose={setSidebarOpen}>
            <Transition.Child
              as={Fragment}
              enter="transition-opacity ease-linear duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="transition-opacity ease-linear duration-300"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-gray-900/80" />
            </Transition.Child>

            <div className="fixed inset-0 flex">
              <Transition.Child
                as={Fragment}
                enter="transition ease-in-out duration-300 transform"
                enterFrom="-translate-x-full"
                enterTo="translate-x-0"
                leave="transition ease-in-out duration-300 transform"
                leaveFrom="translate-x-0"
                leaveTo="-translate-x-full"
              >
                <Dialog.Panel className="relative flex w-full max-w-xs flex-1">
                  <div className="absolute top-0 right-0 -mr-16 pt-2">
                    <button
                      type="button"
                      className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                      onClick={() => setSidebarOpen(false)}
                    >
                      <span className="sr-only">Close sidebar</span>
                      <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
                    </button>
                  </div>
                  <div className="flex h-full flex-col overflow-y-auto bg-white dark:bg-gray-800 py-6 shadow-xl">
                    <div className="px-4 sm:px-6">
                      <Dialog.Title className="text-lg font-medium text-gray-900 dark:text-white">Menu</Dialog.Title>
                    </div>
                    <div className="mt-6 relative flex-1 px-4 sm:px-6">
                      <nav className="flex flex-1 flex-col divide-y divide-gray-200 dark:divide-gray-700">
                        <div className="space-y-1">
                          {navigation.map((item) => (
                            <a
                              key={item.name}
                              href={item.href}
                              className={classNames(
                                item.current ? 'bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white' : 'text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 dark:text-gray-200',
                                'group flex items-center px-3 py-2 text-sm font-medium rounded-md'
                              )}
                              aria-current={item.current ? 'page' : undefined}
                            >
                              <item.icon
                                className={classNames(
                                  item.current ? 'text-gray-500 dark:text-gray-300' : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300',
                                  'mr-3 flex-shrink-0 h-6 w-6'
                                )}
                                aria-hidden="true"
                              />
                              {item.name}
                            </a>
                          ))}
                        </div>
                      </nav>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </Dialog>
        </Transition.Root>

        {/* Static sidebar for desktop */}
        <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-16 lg:flex-col font-sans dark:text-white">
          <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-black px-6 pb-4 dark:text-white">
            <div className="flex h-16 shrink-0 items-center">
              <p className='font-sans font-bold text-xl ml-2'>S</p>
            </div>
            <nav className="flex flex-1 flex-col dark:text-white">
              <ul role="list" className="flex flex-1 flex-col gap-y-7">
                <li>
                  <ul role="list" className="-mx-2 space-y-1">
                    {navigation.map((item) => (
                      <li key={item.name}>
                        <a
                          href={item.href}
                          className={classNames(
                            item.current
                              ? 'bg-gray-50 text-red-600'
                              : 'text-gray-700 dark:text-white hover:text-red-600 hover:bg-gray-50 font-sans dark:text-white font-light',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold font-sans dark:text-white font-light'
                          )}
                        >
                          <item.icon
                            className={classNames(
                              item.current ? 'text-red-600' : 'text-gray-400 group-hover:text-red-600',
                              'h-6 w-6 shrink-0'
                            )}
                            aria-hidden="true"
                          />
                        </a>
                      </li>
                    ))}
                  </ul>
                </li>
              </ul>
            </nav>
          </div>
        </div>

        <div className="lg:pl-16">
          <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white dark:bg-gray-900 px-4 shadow-lg sm:gap-x-6 sm:px-6 lg:px-8 font-sans dark:text-white">
            <button type="button" className="-m-2.5 p-2.5 text-gray-700 lg:hidden" onClick={() => setSidebarOpen(true)}>
              <span className="sr-only">Open sidebar</span>
              <Bars3Icon className="h-6 w-6" aria-hidden="true" />
            </button>

            {/* Separator */}
            <div className="h-6 w-px bg-gray-200 lg:hidden" aria-hidden="true" />

            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6 ">
              <form className="relative flex flex-1" action="#" method="GET">
                <label htmlFor="search-field" className="sr-only">
                  Search
                </label>
                <MagnifyingGlassIcon
                  className="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400"
                  aria-hidden="true"
                />
                <input
                  id="search-field"
                  className="block h-full w-full border-0 py-0 pl-8 pr-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm bg-white dark:bg-gray-900"
                  placeholder="Search..."
                  type="search"
                  name="search"
                />
              </form>
              <div className="flex items-center gap-x-4 lg:gap-x-6">
                <DarkModeToggle />  

                {/* Separator */}
                <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" aria-hidden="true" />

                {/* Profile dropdown */}
                <Menu as="div" className="relative">
                  <Menu.Button className="-m-1.5 flex items-center p-1.5">
                    <span className="sr-only">Open user menu</span>
                    <img
                      className="h-8 w-8 rounded-full bg-gray-50"
                      src={userPhoto}
                      alt="User Photo decorative"
                    />
                    <span className="hidden lg:flex lg:items-center">
                      <span className="ml-4 text-sm font-semibold leading-6 text-gray-900 dark:text-white" aria-hidden="true">
                        {userFullName}
                      </span>
                      <ChevronDownIcon className="ml-2 h-5 w-5 text-gray-400" aria-hidden="true" />
                    </span>
                  </Menu.Button>
                  <Transition
                    as={Fragment}
                    enter="transition ease-out duration-100"
                    enterFrom="transform opacity-0 scale-95"
                    enterTo="transform opacity-100 scale-100"
                    leave="transition ease-in duration-75"
                    leaveFrom="transform opacity-100 scale-100"
                    leaveTo="transform opacity-0 scale-95"
                  >
                    <Menu.Items className="absolute right-0 z-10 mt-2.5 w-32 origin-top-right rounded-md bg-white dark:bg-gray-900 py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none dark:text-white">
                      {userNavigation.map((item) => (
                        <Menu.Item key={item.name}>
                          {({ active }) => (
                            <a
                              href={item.href}
                              className={classNames(
                                active ? 'bg-gray-50 dark:bg-red-600' : '',
                                'block px-3 py-1 text-sm leading-6 text-gray-900 dark:text-white'
                              )}
                              onClick={(event) => handleMenuClick(event, item.name)}
                            >
                              {item.name}
                            </a>
                          )}
                        </Menu.Item>
                      ))}
                    </Menu.Items>
                  </Transition>
                </Menu>
              </div>
            </div>
          </div>

          <AdBanner />

          <main className="py-0">
            <div className="px-0 dark:bg-gray-900">
              {children} 
            </div>
          </main>
        </div>
      </div>
    </>
  )
}
