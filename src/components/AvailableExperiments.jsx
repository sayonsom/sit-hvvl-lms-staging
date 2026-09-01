import { EllipsisVerticalIcon } from '@heroicons/react/20/solid'

const projects = [
  { name: 'Impulse Voltage Generator', initials: 'IV', href: '/project', members: 1, bgColor: 'bg-pink-600' },
  { name: 'Cockroft-Walton', initials: 'CW', href: '/project', members: 45, bgColor: 'bg-purple-600' },
  { name: 'Partial Discharge', initials: 'PD', href: '/not-in-demo', members: 20, bgColor: 'bg-yellow-500' }
]

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function AvailableExperiments() {
  return (
    <div className=''>
      {/* <h2 className="text-sm font-medium text-gray-500">Pinned Projects</h2> */}
      <ul role="list" className="mt-3 grid grid-cols-1 gap-5 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
        {projects.map((project) => (
          <li key={project.name} className="col-span-1 flex rounded-md shadow-sm">
            <div
              className={classNames(
                project.bgColor,
                'flex w-16 flex-shrink-0 items-center justify-center rounded-l-md text-sm font-medium text-white'
              )}
            >
              {project.initials}
            </div>
            <div className="flex flex-1 items-center justify-between truncate rounded-r-md border-b border-r border-t border-gray-200 dark:border-gray-900 bg-white dark:bg-gray-800 font-sans">
              <div className="flex-1 truncate px-4 py-2 text-sm">
                <a href={project.href} className="font-medium text-gray-900 dark:text-white hover:text-gray-600 hover:text-gray-200">
                  {project.name}
                </a>
                <p className="text-gray-500">{project.members} Devices</p>
              </div>
              <div className="flex-shrink-0 pr-2">
                <button
                  type="button"
                  className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-transparent bg-white dark:bg-gray-700 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  <span className="sr-only">Open options</span>
                  <EllipsisVerticalIcon className="h-5 w-5 " aria-hidden="true" />
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
